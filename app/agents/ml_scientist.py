from app.agents.base import BaseAgent
from app.prompts.personas import PRIYA_PROMPT


class PriyaAgent(BaseAgent):
    name = "Aayush Koirala"
    role = "ml_scientist"
    system_prompt = PRIYA_PROMPT
    preferred_provider = "gemini"
