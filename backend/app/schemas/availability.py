
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator


class AvailabilitySlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_slot_time(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self


class AvailabilitySlotResponse(BaseModel):
    id: int
    doctor_id: int
    start_time: datetime
    end_time: datetime

    model_config = ConfigDict(from_attributes=True)
