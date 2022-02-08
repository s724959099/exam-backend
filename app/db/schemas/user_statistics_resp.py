"""StatisticsResponse schemas"""

from pydantic import BaseModel, Field


class StatisticsResponse(BaseModel):
    """
    StatisticsResponse
    """
    sign_up_count: int = Field(
        ...,
        description='Total number of users who have signed up')
    today_active_count: int = Field(
        ...,
        description='Total number of users with active sessions today')
    last_7days_active_avg: float = Field(
        ...,
        # pylint: disable-next=line-too-long
        description='Average number of active session users in the last 7 days rolling'
    )
