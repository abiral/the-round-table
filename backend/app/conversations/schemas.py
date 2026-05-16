from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


ConversationStatus = Literal["in_progress", "awaiting_user", "concluded"]


class ConversationListItem(BaseModel):
    id: str
    title: str
    status: ConversationStatus
    last_message_at: datetime


class ConversationDetail(BaseModel):
    id: str
    title: str
    status: ConversationStatus
    last_message_at: datetime
    state: dict[str, Any]
