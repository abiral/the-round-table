from app.agents.base import BaseAgent
from app.prompts.personas import SANTOSH_PROMPT


class SantoshAgent(BaseAgent):
    name = "Santosh Poudel"
    role = "php_plugin"
    system_prompt = SANTOSH_PROMPT
