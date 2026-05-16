from app.agents.base import BaseAgent
from app.prompts.personas import SUVASH_PROMPT


class SuvashAgent(BaseAgent):
    name = "Suvash BK"
    role = "wp_plugin_reviewer"
    system_prompt = SUVASH_PROMPT
