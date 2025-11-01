import uuid
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .general_data_elements import UUID_NAMESPACE


class PayerPlan(BaseModel):
    file_id: str = Field(..., description="The file identifier for the hospital price transparency file.")
    plan_id: Optional[str] = Field(default=None, description="The unique identifier for the payer’s specific plan associated with the standard charge.")
    payer_name: str = Field(..., description="The name of the payer associated with the negotiated charge for the item or service.")
    plan_name: str = Field(..., description="The name of the payer’s specific plan associated with the standard charge.")

    @model_validator(mode='after')
    def set_plan_id(self) -> 'PayerPlan':
        if not self.plan_id:
            self.plan_id = uuid.uuid5(UUID_NAMESPACE, f"{self.payer_name}-{self.plan_name}").hex
        return self
