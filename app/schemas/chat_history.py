from pydantic import BaseModel


class ChatHistoryBase(BaseModel):
    user_id: int
    session_id: str
    question: str
    answer: str


class ChatHistoryCreate(ChatHistoryBase):
    pass
