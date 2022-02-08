"""MessageResponse schemas"""

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """
    MessageResponse
    """
    msg: str = Field(..., description='Message response')
