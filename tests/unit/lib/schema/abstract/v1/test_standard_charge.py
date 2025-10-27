from hpt_converter.lib.schema.abstract.v1 import StandardCharge
from uuid import uuid4
from pydantic import ValidationError
import pytest



def _get_standard_charge() -> dict:
    return {
        "file_id": uuid4().hex,
        "description": "Test Description",
        "codes": [{"code": "12345", "code_type": "CPT"}],
        "setting": "inpatient",
        "drug_unit_of_measurement": "10",
        "drug_type_of_measurement": "gm",
        "gross_charge": 100.00,
        "discounted_cash": 90.00,
        "plan_id": uuid4().hex,
        "negotiated_dollar": 80.00,
        "negotiated_percentage": 80.00,
        "estimated_amount": 80.00,
        "min_charge": 70.00,
        "max_charge": 120.00,
        "methodology": "fee schedule"
    }


def test_standard_charge():
    # Arrange
    data = _get_standard_charge()
    
    # Act
    sc = StandardCharge(**data)
    
    # Assert
    assert sc.model_dump(exclude_none=True) == data


def test_invalid_code_type():
    # Arrange
    data = _get_standard_charge()
    data['codes'] = [{"code": "12345", "code_type": "INVALID"}]
    
    # Act & Assert
    with pytest.raises(ValidationError, match="validation error for StandardCharge"):
        StandardCharge(**data)


def test_invalid_setting():
    # Arrange
    data = _get_standard_charge()
    data['setting'] = "invalid_setting"
    
    # Act & Assert
    with pytest.raises(ValidationError, match="validation error for StandardCharge"):
        StandardCharge(**data)


def test_invalid_measurement_type():
    # Arrange
    data = _get_standard_charge()
    data['drug_type_of_measurement'] = "invalid_type"
    
    # Act & Assert
    with pytest.raises(ValidationError, match="validation error for StandardCharge"):
        StandardCharge(**data)

def test_invalid_methodology():
    # Arrange
    data = _get_standard_charge()
    data['methodology'] = "invalid_methodology"
    
    # Act & Assert
    with pytest.raises(ValidationError, match="validation error for StandardCharge"):
        StandardCharge(**data)
