import uuid
from typing import Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator

StateAbbreviations = {
    'alabama': 'AL',
    'alaska': 'AK',
    'arizona': 'AZ',
    'arkansas': 'AR',
    'california': 'CA',
    'colorado': 'CO',
    'connecticut': 'CT',
    'delaware': 'DE',
    'florida': 'FL',
    'georgia': 'GA',
    'hawaii': 'HI',
    'idaho': 'ID',
    'illinois': 'IL',
    'indiana': 'IN',
    'iowa': 'IA',
    'kansas': 'KS',
    'kentucky': 'KY',
    'louisiana': 'LA',
    'maine': 'ME',
    'maryland': 'MD',
    'massachusetts': 'MA',
    'michigan': 'MI',
    'minnesota': 'MN',
    'mississippi': 'MS',
    'missouri': 'MO',
    'montana': 'MT',
    'nebraska': 'NE',
    'nevada': 'NV',
    'new hampshire': 'NH',
    'new jersey': 'NJ',
    'new mexico': 'NM',
    'new york': 'NY',
    'north carolina': 'NC',
    'north dakota': 'ND',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'rhode island': 'RI',
    'south carolina': 'SC',
    'south dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'vermont': 'VT',
    'virginia': 'VA',
    'washington': 'WA',
    'west virginia': 'WV',
    'wisconsin': 'WI',
    'wyoming': 'WY',
    'district of columbia': 'DC',
    'american samoa': 'AS',
    'guam': 'GU',
    'northern mariana islands': 'MP',
    'commonwealth of the northern mariana islands': 'MP',
    'puerto rico': 'PR',
    'u.s. virgin islands': 'VI'
}


UUID_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, 'https://github.com/kennytro/hpt_converter')

class GeneralDataElements(BaseModel):
    file_id: Optional[str] = Field(default=None, description="The file identifier for the hospital price transparency file.")
    hospital_name: str = Field(..., description="The legal business name of the licensee.")
    last_updated_on: str = Field(..., description="Date on which the MRF was last updated. Date must be in an ISO 8601 format (i.e. YYYY-MM-DD).")
    version: str = Field(..., description="The version of the CMS Template used.")
    hospital_location: str = Field(..., description="The unique name of the hospital location absent any acronyms.")
    hospital_address: str = Field(..., description="The geographic address of the corresponding hospital location.")
    license_number: Tuple[str, str] = Field(description="The hospital license number and the licensing state or territory’s two-letter abbreviation for the hospital location(s) indicated in the file.")
    affirmation_statement: bool = Field(..., description="Required affirmation statement.")
    financial_aid_policy: Optional[str] = Field(default=None, description="The hospital’s financial aid policy.")
    general_contract_provisions: Optional[str] = Field(default=None, description="Payer contract provisions that are negotiated at an aggregate level across items and services (e.g., claim level).")

    @field_validator('license_number')
    @classmethod
    def validate_license_number(cls, value: Tuple[str, str]) -> Tuple[str, str]:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("license_number must be a list or tuple of two elements: [license_number, state_abbreviation]")
        license_num = value[0]
        state = value[1].upper()    # transform to upper case
        if state not in StateAbbreviations.values():
            raise ValueError(f"Invalid state abbreviation: {state}")
        if not license_num or not isinstance(license_num, str):
            raise ValueError(f"Invalid license number for state {state}: {license_num}")
        return (license_num, state)

    @model_validator(mode='after')
    def set_file_id(self) -> 'GeneralDataElements':
        if not self.file_id:
            self.file_id = uuid.uuid5(UUID_NAMESPACE, f"{self.hospital_name}-{self.last_updated_on}-{self.version}-{self.hospital_location}-{self.hospital_address}").hex
        return self
