from app.agents.base import BaseAgent
from app.prompts.personas import LENA_PROMPT


class LenaAgent(BaseAgent):
    name = "Prakriti Bhandari"
    role = "qa"
    system_prompt = LENA_PROMPT
