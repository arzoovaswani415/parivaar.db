from pydantic import ConfigDict
from datetime import datetime,time
from pydantic import BaseModel, Field
from typing import Optional
from app.enums.reminder import ReminderType, ReminderFrequency, ReminderStatus

class ReminderCreate(BaseModel):
    family_member_id: int = Field(..., alias="familyMemberId")
    title: str
    description: Optional[str] = None
    type: ReminderType
    frequency: ReminderFrequency
    time_of_day: time = Field(alias="timeOfDay") # Format: "HH:MM" (UTC)
    start_date: Optional[datetime] = Field(None, alias="startDate")

    model_config = ConfigDict(
        populate_by_name=True
    )


class ReminderResponse(BaseModel):
    id: int
    family_member_id: int = Field(..., alias="familyMemberId")
    family_member_name: Optional[str] = Field(None, alias="familyMemberName")
    title: str
    description: Optional[str] = None
    type: ReminderType
    frequency: ReminderFrequency
    time_of_day: str = Field(..., alias="timeOfDay")
    start_date: datetime = Field(..., alias="startDate")
    next_trigger_at: datetime = Field(..., alias="nextTriggerAt")
    last_triggered_at: Optional[datetime] = Field(None, alias="lastTriggeredAt")
    status: ReminderStatus
    active_yn: bool = Field(..., alias="active")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
