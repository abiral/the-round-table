from app.agents.base import BaseAgent
from app.prompts.personas import RAKESH_PROMPT


class RakeshAgent(BaseAgent):
    name = "Rakesh Tandulkar"
    role = "wp_theme_reviewer"
    system_prompt = RAKESH_PROMPT
