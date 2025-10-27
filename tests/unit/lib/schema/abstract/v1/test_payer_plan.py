from hpt_converter.lib.schema.abstract.v1 import PayerPlan
from uuid import uuid4


def _get_payer_plan() -> dict:
    return {
        "file_id": uuid4().hex,
        "payer_name": "Test Payer",
        "plan_name": "Test Plan"
    }


def test_payer_plan():
    # Arrange
    data = _get_payer_plan()
    
    # Act
    pp = PayerPlan(**data)
    
    # Assert
    assert pp.plan_id is not None
    assert pp.model_dump() == data | {"plan_id": pp.plan_id}