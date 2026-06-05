from pydantic import BaseModel, ConfigDict
from typing import Optional


class urlMetricRequest(BaseModel):
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class urlMetricDayResponse(BaseModel):
    day: int
    month: int
    year: int
    amount: int

    model_config = ConfigDict(from_attributes=True)

class urlMetricMonthResponse(BaseModel):
    month: int
    year: int
    amount: int

    model_config = ConfigDict(from_attributes=True)

class urlMetricYearResponse(BaseModel):
    year: int
    amount: int

    model_config = ConfigDict(from_attributes=True) 
