from uglygpt.base import config, logger
from uglygpt.memory import get_memory
from uglygpt.provider import get_llm_provider, LLMProvider
from uglygpt.agent.json_utils import fix_json_using_multiple_techniques
from uglygpt.agent.prompt import AgentPrompt

format_prompt = AgentPrompt()

def _validate_json(json_string: str):
    try:
        response = fix_json_using_multiple_techniques(json_string)
        return response
    except:
        return False

def execution(task: str, llm: LLMProvider = get_llm_provider() , memory = get_memory(config), context_results: int = 1) -> str:
    if context_results > 0:
        context = memory.get_relevant(task, context_results)
        if context != "":
            format_prompt.add(f"Take into account these previously completed tasks: {str(context)}")
    commands_prompt = ""
    prompt = format_prompt("execute", task=task, COMMANDS=commands_prompt)

    response = llm.instruct(prompt)
    valid_json = _validate_json(response)
    while not valid_json:
        logger.error("INVALID JSON RESPONSE",response)
        logger.info("... Trying again.")
        response = llm.instruct(prompt)
        valid_json = _validate_json(response)
    if valid_json:
        response = valid_json
    response_parts = []
    if "plan" in response:
        response_parts.append(f"\n\nPLAN:\n\n{response['plan']}")
    if "summary" in response:
        response_parts.append(f"\n\nSUMMARY:\n\n{response['summary']}")
    if "response" in response:
        response_parts.append(f"\n\nRESPONSE:\n\n{response['response']}")
    if "command" in response:
        command = response["command"]
        response_parts.append(f"\n\nCOMMAND:\n\n{command}")
        for command_name, command_args in command.items():
            # Search for the command in the available_commands list, and if found, use the command's name attribute for execution
            if command_name is not None:
                """ for available_command in self.available_commands:
                    if command_name in [
                        available_command["friendly_name"],
                        available_command["name"],
                    ]:
                        command_name = available_command["name"]
                        break """
                """ try:
                    response_parts.append(f"\n\n{self.commands.call(command_name, **command_args)}")
                except:
                    pass """
                pass
            else:
                if command_name == "None.":
                    response_parts.append(f"\n\nNo commands were executed.")
                else:
                    response_parts.append(
                        f"\n\nCommand not recognized: {command_name}"
                    )
    response = "".join(response_parts)
    if context_results > 0:
        memory.add(response.strip())
    return response
