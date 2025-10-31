from hpt_converter.lib.schema.json.v2.hpt import HospitaPriceTransparency, LicenseInformation, State
import json
from pathlib import Path

def test_model(data_root: Path):
    # Arrange
    with open(data_root.joinpath('json', 'test_v2.json')) as file:
        data = json.load(file)

    # Act
    htp = HospitaPriceTransparency(**data)
    
    # Assert
    assert htp.hospital_name == 'West Mercy Hospital'
    assert htp.license_information == LicenseInformation(license_number='50056', state=State.CA)
    assert len(htp.standard_charge_information) == 11
