from app.agents.base import BaseAgent
from app.prompts.personas import SHREYA_PROMPT


class ShreyaAgent(BaseAgent):
    name = "Shreya Manandhar"
    role = "php_theme"
    system_prompt = SHREYA_PROMPT
