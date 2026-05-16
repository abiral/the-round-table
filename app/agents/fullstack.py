from app.agents.base import BaseAgent
from app.prompts.personas import ETHAN_PROMPT


class EthanAgent(BaseAgent):
    name = "Samriddhi Neupane"
    role = "fullstack"
    system_prompt = ETHAN_PROMPT
    preferred_provider = "gemini"
