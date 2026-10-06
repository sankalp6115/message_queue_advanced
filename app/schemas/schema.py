from typing import Literal, Annotated, Union
from pydantic import BaseModel, Field, model_validator

class SleepPayload(BaseModel):  
    seconds: int = Field(ge=0,le=300)

class CalculationPayload(BaseModel):
    first: int = Field(ge=-1_000_000,le=1_000_000)
    second: int = Field(ge=-1_000_000,le=1_000_000)
    operator: Literal["+","-","*","/","//","**"]


    # model validator used for custom validation logic for a complete model
    @model_validator(mode="after")
    def validate_exponent(self):
        if self.operator == "**" and not self.second <= 8:
            raise ValueError(
                "For Exponentiation, power must be between 0 and 8"
            )

        return self

class SleepJobRequest(BaseModel):
    type: Literal["sleep"]
    payload: SleepPayload

class CalculationJobRequest(BaseModel):
    type: Literal["calculation"]
    payload: CalculationPayload

JobRequest = Annotated[
    Union[SleepJobRequest,CalculationJobRequest],
    Field(discriminator="type"),
]

#type = "sleep"        → FastAPI validates SleepPayload
#type = "calculation"  → FastAPI validates CalculationPayload
#any other type        → FastAPI rejects the request
