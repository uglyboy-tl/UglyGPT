from dataclasses import dataclass

from uAgent.base import logger
from uAgent.agents.action import Action
from uAgent.chains.prompt import PromptTemplate

@dataclass
class DesignReview(Action):
    name: str = "DesignReview"
    role: str = "Role: You are a senior engineer; the goal is to review the design of the API, and give feedback on whether the design meets the requirements of the PRD and whether it complies with good design practices"
    filename: str = "docs/design.md"

    def run(self, prd, api_design):
        logger.info(f'Design Review..')
        self.llm.set_prompt(PromptTemplate(f"Here is the Product Requirement Document (PRD):\n\n{prd}\n\nHere is the list of APIs designed " \
                f"based on this PRD:\n\n{api_design}\n\nPlease review whether this API design meets the requirements" \
                f" of the PRD, and whether it complies with good design practices."))

        self._ask(prd = prd, api_design=api_design)