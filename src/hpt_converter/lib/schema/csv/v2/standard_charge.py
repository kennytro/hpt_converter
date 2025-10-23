import csv
from decimal import Decimal
from typing import Dict, List, Optional, get_type_hints, Type

from pydantic import BaseModel, Field, create_model, field_validator

from hpt_converter.lib.csv.utils import get_csv_type, normalize_header
from hpt_converter.lib.schema.csv import CsvType

StandardChargeBaseFields = {
    'description': (str, ...),
    'setting': (str, ...),
    'drug_unit_of_measurement': (str, None),
    'drug_type_of_measurement': (str, None),
    'standard_charge|gross': (Optional[Decimal], Field(default=None, max_digits=16, decimal_places=2)),
    'standard_charge|discounted_cash': (Optional[Decimal], Field(default=None, max_digits=16, decimal_places=2)),
    'modifiers': (str, None),
    'standard_charge|min': (Optional[Decimal], Field(default=None, max_digits=16, decimal_places=2)),
    'standard_charge|max': (Optional[Decimal], Field(default=None, max_digits=16, decimal_places=2)),
    'additional_generic_notes': (str, None)   
}


def get_standard_charge_base_fields(csv_type: CsvType) -> dict:
    """Returns the base fields for StandardCharge based on the CSV type.
    Args:
        csv_type (CsvType): The type of the CSV file (tall or wide).
    Returns:
        dict: A dictionary of field names and their types for StandardCharge."""
    additional_fields = {
        'plan_ids': (List[str], None)
    }
    if csv_type == CsvType.TALL:
        additional_fields = additional_fields | {
            'payer_name': (str, None),
            'plan_name': (str, None),
            'standard_charge|negotiated_dollar': (Optional[Decimal], Field(default=None, max_digits=10, decimal_places=2)),
            'standard_charge|negotiated_percentage': (Optional[Decimal], Field(default=None, max_digits=5, decimal_places=2)),
            'standard_charge|negotiated_algorithm': (str, None),
            'estimated_amount': (Optional[Decimal], Field(default=None, max_digits=10, decimal_places=2)),
            'standard_charge|methodology': (str, None)
        }
    # wide type has no additional fields.

    return StandardChargeBaseFields | additional_fields



def create_standard_charge_model(csv_file_path: str) -> BaseModel:
    """Creates and returns the appropriate StandardCharge model class based on the CSV type.

    Args:
        csv_file_path (str): Path to the CSV file.

    Returns:
        BaseModel: The corresponding StandardCharge model class."""

    def _create_validator(fields: Dict) -> Dict:
        validators = {}
        for field, field_tuple in fields.items():
            if field_tuple[0] == Optional[Decimal]:
                validators[f'{field}_validator'] = field_validator(field, mode='before')(lambda cls, v: v if v != '' else None)
        
        return validators
    # def default_decimal(cls, v):
    #     return v if v != '' else None

    standard_charge_header = []
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        for _ in range(3):
            standard_charge_header = next(csv_reader, None)

    if not standard_charge_header:
        raise ValueError(f"CSV file({csv_file_path}) is missing standard chage header line.")

    standard_charge_header = normalize_header(standard_charge_header)
    csv_type = get_csv_type(standard_charge_header)
    fields = get_standard_charge_base_fields(csv_type)
    # dynamically add placeholder fields.
    for field_name in {x for x in standard_charge_header if x not in fields}:
        if (field_name.endswith('negotiated_dollar') or
                field_name.endswith('negotiated_percentage') or 
                field_name.startswith('estimated_amount|')):
            fields[field_name] = (Decimal, None)
        else:
            fields[field_name] = (str, None)
    
    return create_model('StandardChargeDynamicModel', **fields,
                        __validators__=_create_validator(fields)
                        # __validators__={'standard_charge|gross_validator': field_validator('standard_charge|gross', mode='before')(default_decimal)}
    )
