from decimal import Decimal
from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


class DrugTypeOfMeasument(StrEnum):
    GRAM = 'gm'
    GRAMS = 'gr'
    MILLIGRAMS = 'me'
    MILLILITERS = 'ml'
    UNIT = 'un'
    INTERNATIONAL_UNITS = 'f2'
    EACH = 'ea'


class StandardChargeMethod(StrEnum):
    CASE_RATE = 'case rate'
    FEE_SCHEDULE = 'fee schedule'
    PERCENT_OF_TOTAL_BILLED_CHARGES = 'percent of total billed charges'
    PER_DIEM = 'per diem'
    OTHER = 'other'


class Setting(StrEnum):
    INPATIENT = 'inpatient'
    OUTPATIENT = 'outpatient'
    BOTH = 'both'


class CodeType(StrEnum):
    CURRENT_PROCEDURAL_TERMINOLOGY = 'CPT'
    NATIONAL_DRUG_CODE = 'NDC'
    HEALTHCRE_COMMON_PROCEDURAL_CODING_SYSTEM = 'HCPCS'
    REVENUE_CODE = 'RC'
    INTERNATIONAL_CLASSIFICATION_OF_DISEASES = 'ICD'
    DIAGNOSIS_RELATED_GROUPS = 'DRG'
    Medicare_Severity_Diagnosis_Related_Groups = 'MS-DRG'
    REFINED_DIAGNOSIS_RELATED_GROUPS = 'R-DRG'
    SEVERITY_DIAGNOSIS_RELATED_GROUPS = 'S-DRG'
    ALL_PATIENT_SEVERITY_ADJUSTED_DIAGNOSIS_RELATED_GROUPS = 'APS-DRG'
    ALL_PATIENT_DIAGNOSIS_RELATED_GROUPS = 'AP-DRG'
    ALL_PATIENT_REFINED_DIAGNOSIS_RELATED_GROUPS = 'APR-DRG'
    AMBULATORY_PAYMENT_CLASSIFICATIONS = 'APC'
    LOCAL_CODE_PROCESSING = 'LOCAL'
    ENHANCED_AMBULATORY_PATIENT_GROUPING = 'EAPG'
    HEALTH_INSURANCE_PROSPECTIVE_PAYMENT_SYSTEM = 'HIPPS'
    CURRENT_DENTAL_TERMINOLOGY = 'CDT'
    CHARGE_DESCRIPTION_MASTER = 'CDM'
    TRICARE_DIAGNOSIS_RELATED_GROUPS = 'TRIS-DRG'


class CodeInformation(BaseModel):
    code: str = Field(..., description="Any code used by the hospital for purposes of billing or accounting for the item or service.")
    code_type: CodeType = Field(..., description="The associated coding type for the 'Code' data element.")


class StandardCharge(BaseModel):
    file_id: str = Field(..., description="The file identifier for the hospital price transparency file.")
    description: str = Field(..., description="Description of each item or service provided by the hospital that corresponds to the standard charge the hospital has established.")
    codes: List[CodeInformation] = Field(default=[], description="Any code(s) and type(s) used by the hospital for purposes of billing or accounting for the item or service. .")
    setting: Setting = Field(..., description="Indicates whether the item or service is provided in connection with an inpatient admission or an outpatient department visit. ")
    drug_unit_of_measurement: Optional[str] = Field(default=None, description="If the item or service is a drug, indicate the unit value that corresponds to the established standard charge..")
    drug_type_of_measurement: Optional[DrugTypeOfMeasument] = Field(default=None, description="The measurement type that corresponds to the established standard charge for drugs as defined by either the National Drug Code or the National Council for Prescription Drug Programs. ")
    gross_charge: Optional[Decimal] = Field(default=None, alias='standard_charge|gross',
                                  description="Gross charge is the charge for an individual item or service that is reflected on a hospital’s chargemaster, absent any discounts.")
    discounted_cash: Optional[Decimal] = Field(default=None, alias='standard_charge|discounted_cash', 
                                               description="The discounted cash price for the item or service.")
    plan_id: str = Field(default=None, description="The unique identifier for the payer’s specific plan associated with the negotiated charge.")
    modifiers: Optional[str] = Field(default=None, description="Include any modifier(s) that may change the standard charge that corresponds to hospital items or services.")
    negotiated_dollar: Optional[Decimal] = Field(default=None, description="Payer-specific negotiated charge (expressed as a dollar amount) that a hospital has negotiated with a third-party payer for the corresponding item or service.")
    negotiated_percentage: Optional[Decimal] = Field(default=None, description="Payer-specific negotiated charge (expressed as a percentage) that a hospital has negotiated with a third-party payer for an item or service.")
    negotiated_algorithm: Optional[str] = Field(default=None, description="Payer-specific negotiated charge (expressed as an algorithm) that a hospital has negotiated with a third-party payer for the corresponding item or service.")
    estimated_amount: Optional[Decimal] = Field(default=None, description="Estimated allowed amount means the average dollar amount that the hospital has historically received from a third party payer for an item or service. If the standard charge is based on a percentage or algorithm, the MRF must also specify the estimated allowed amount for that item or service.")
    min_charge: Optional[Decimal] = Field(default=None, alias='standard_charge|min', 
                                          description="De-identified minimum negotiated charge is the lowest charge that a hospital has negotiated with all third-party payers for an item or service. This is determined from the set of negotiated standard charge dollar amounts.")
    max_charge: Optional[Decimal] = Field(default=None, alias='standard_charge|max',
                                          description="De-identified maximum negotiated charge is the lowest charge that a hospital has negotiated with all third-party payers for an item or service. This is determined from the set of negotiated standard charge dollar amounts.")
    methodology: Optional[StandardChargeMethod] = Field(default=None, description="Method used to establish the payer-specific negotiated charge. The valid value corresponds to the contract arrangement.")
    additional_generic_notes: Optional[str] = Field(default=None, description="A free text data element that is used to help explain any of the data including, for example, blanks due to no applicable data, charity care policies, or other contextual information that aids in the public’s understanding of the standard charges.")   
    additional_payer_notes: Optional[str] = Field(default=None, description="A free text data element used to help explain data in the file that is related to a payer-specific negotiated charge.")    

    model_config = ConfigDict(populate_by_name=True)    # Allow population by the original field name as well

    @field_validator('drug_type_of_measurement', mode='before')
    @classmethod
    def validate_drug_type_of_measurement(cls, value: str) -> Optional[DrugTypeOfMeasument]:
        return value.lower() if (value and value != '') else None
