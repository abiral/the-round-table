from app.agents.base import BaseAgent
from app.prompts.personas import PREM_PROMPT


class PremAgent(BaseAgent):
    name = "Prem Nepali"
    role = "ux_engineer"
    system_prompt = PREM_PROMPT
