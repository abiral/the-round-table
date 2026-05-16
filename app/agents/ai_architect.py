from app.agents.base import BaseAgent
from app.prompts.personas import MAYA_PROMPT


class MayaAgent(BaseAgent):
    name = "Nirajan Sharma"
    role = "ai_architect"
    system_prompt = MAYA_PROMPT
    preferred_provider = "gemini"
