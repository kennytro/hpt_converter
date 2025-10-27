from datetime import date
from uuid import uuid4

import pytest

from hpt_converter.lib.schema.abstract.v1 import GeneralDataElements


def _get_general_data_elements() -> dict:
    return {
        "file_id": uuid4().hex,
        "hospital_name": "Test Hospital",
        "last_updated_on": '2023-10-01',
        "version": "v2.0",
        "hospital_location": "Test Location",
        "hospital_address": "123 Test St, Test City, TS 12345",
        "license_number": ("12345", "CA"),
        "affirmation_statement": True,
        "financial_aid_policy": "This is a test financial aid policy.",
        "general_contract_provisions": "These are test general contract provisions."
    }


def test_general_data_element():
    # Arrange
    data1 = _get_general_data_elements()
    data2 = data1.copy()
    data2['license_number'] = ["12345", "ca"]  # lower case states
    
    # Act & Assert
    for data in (data1, data2):
        gde = GeneralDataElements(**data)
        assert gde.model_dump() == data1


def test_bad_license_number():
    # Arrange
    data1 = _get_general_data_elements()
    data2 = data1.copy()
    data1['license_number'] = ["12345", "XX"]  # Invalid state
    data2['license_number'] = ["", "CA"] # Empty license number
    # Act & Assert
    with pytest.raises(ValueError, match="Invalid state abbreviation: XX"):
        GeneralDataElements(**data1)

    with pytest.raises(ValueError, match="Invalid license number for state CA: "):
        GeneralDataElements(**data2)

def test_auto_file_id():
    # Arrange
    data = _get_general_data_elements()
    data.pop('file_id')
    
    # Act
    gde = GeneralDataElements(**data)
    
    # Assert
    assert gde.file_id is not None