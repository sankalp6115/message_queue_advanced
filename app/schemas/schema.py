from typing import Annotated, Any, Literal, Union
from pydantic import BaseModel, Field, model_validator, ConfigDict
from datetime import datetime
from PIL import Image

# Payload models
class SleepPayload(BaseModel):  
    seconds: int = Field(ge=0,le=300)

class CalculationPayload(BaseModel):
    first: int = Field(ge=-1_000_000,le=1_000_000)
    second: int = Field(ge=-1_000_000,le=1_000_000)
    operator: Literal["+","-","*","/","//","**"]


    # model validator used for custom validation logic for a complete model
    @model_validator(mode="after")
    def validate_exponent(self):
        if self.operator == "**" and not 0 <= self.second <= 8:
            raise ValueError(
                "For Exponentiation, power must be between 0 and 8"
            )

        return self

class ImagePayload(BaseModel):
    image_path: str
    # operation: Literal["compress","resize","classify"]
    operation: str = "compress"


# Request models
class SleepJobRequest(BaseModel):
    type: Literal["sleep"]
    payload: SleepPayload

class CalculationJobRequest(BaseModel):
    type: Literal["calculation"]
    payload: CalculationPayload

class ImageJobRequest(BaseModel):
    type: Literal["image"]
    payload: ImagePayload


JobRequest = Annotated[
    Union[SleepJobRequest,CalculationJobRequest,ImageJobRequest],
    Field(discriminator="type"),
]

JobStatus = Literal["pending","running","failed","completed"]

# response model
class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    payload: dict[str, Any]
    status: JobStatus
    result: dict[str, Any] | list[Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
