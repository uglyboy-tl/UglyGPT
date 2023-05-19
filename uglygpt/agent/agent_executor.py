import time
from typing import Any, List, Dict, Tuple, Callable, Optional, Sequence, Union
from dataclasses import dataclass, field

from uglygpt.chain.base import Chain
from uglygpt.tools.base import BaseTool
from uglygpt.prompts.output_parsers.base import OutputParserException
from uglygpt.agent.agent import Agent, BaseSingleActionAgent
from uglygpt.agent.schema import AgentAction, AgentFinish
from uglygpt.agent.tools import InvalidTool

@dataclass
class AgentExecutor(Chain):
    """Consists of an agent using tools."""
    agent: BaseSingleActionAgent = field(default_factory=Agent)
    tools: Sequence[BaseTool] = field(default_factory=list)
    return_intermediate_steps: bool = False
    max_iterations: Optional[int] = 15
    max_execution_time: Optional[float] = None

    @property
    def input_keys(self) -> List[str]:
        """Return the input keys.

        :meta private:
        """
        return self.agent.input_keys

    @property
    def output_keys(self) -> List[str]:
        """Return the singular output key.

        :meta private:
        """
        if self.return_intermediate_steps:
            return self.agent.return_values + ["intermediate_steps"]
        else:
            return self.agent.return_values

    def _should_continue(self, iterations: int, time_elapsed: float) -> bool:
        if self.max_iterations is not None and iterations >= self.max_iterations:
            return False
        if (
            self.max_execution_time is not None
            and time_elapsed >= self.max_execution_time
        ):
            return False

        return True

    def _take_next_step(self, name_to_tool_map: Dict[str, BaseTool], inputs: Dict[str, str], intermediate_steps: List[Tuple[AgentAction, str]] ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:
        """Take a single step in the thought-action-observation loop.

        Override this to take control of how the agent makes and acts on choices.
        """
        try:
            # Call the LLM to see what to do.
            output = self.agent.plan(
                intermediate_steps,
                **inputs,
            )
        except OutputParserException as e:
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                raise e
            text = str(e)
            if isinstance(self.handle_parsing_errors, bool):
                observation = "Invalid or incomplete response"
            elif isinstance(self.handle_parsing_errors, str):
                observation = self.handle_parsing_errors
            elif callable(self.handle_parsing_errors):
                observation = self.handle_parsing_errors(e)
            else:
                raise ValueError("Got unexpected type of `handle_parsing_errors`")
            output = AgentAction("_Exception", observation, text)
            return [(output, observation)]
        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            return output
        actions: List[AgentAction]
        if isinstance(output, AgentAction):
            actions = [output]
        else:
            actions = output
        result = []
        for agent_action in actions:
            if agent_action.tool in name_to_tool_map:
                tool = name_to_tool_map[agent_action.tool]
                return_direct = tool.return_direct
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                if return_direct:
                    tool_run_kwargs["llm_prefix"] = ""
                # We then call the tool on the tool input to get an observation
                observation = tool.run(
                    agent_action.tool_input,
                    **tool_run_kwargs,
                )
            else:
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                observation = InvalidTool().run(
                    agent_action.tool,
                    **tool_run_kwargs,
                )
            result.append((agent_action, observation))
        return result

    def _execute(self, inputs: Dict[str, str]) -> Dict[str, Any]:
        """Run text through and get agent response."""

        name_to_tool_map = {tool.name: tool for tool in self.tools}
        intermediate_steps: List[Tuple[AgentAction, str]] = []
        # Let's start tracking the number of iterations and time elapsed
        iterations = 0
        time_elapsed = 0.0
        start_time = time.time()

        # We now enter the agent loop (until it returns something).
        while self._should_continue(iterations, time_elapsed):
            next_step_output = self._take_next_step(
                name_to_tool_map,
                inputs,
                intermediate_steps,
            )
            if isinstance(next_step_output, AgentFinish):
                return next_step_output.return_values

            intermediate_steps.extend(next_step_output)
            iterations += 1
            time_elapsed = time.time() - start_time
        return {"reason":"Stopped"}