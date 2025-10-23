from hpt_converter.lib.csv.utils import CsvType
from hpt_converter.lib.schema.csv.v2.standard_charge import get_standard_charge_base_fields
from pydantic import create_model
from decimal import Decimal

def create_standard_charge_instance(csv_type: CsvType):

    fields = get_standard_charge_base_fields(csv_type)
    model_data = {
        'description': 'Test Description',
        'setting': 'inpatient',
        'drug_unit_of_measurement': '10',
        'drug_type_of_measurement': 'gm',
        'code|1': '12345',
        'code|1|type': 'CPT',
        'standard_charge|gross': Decimal('100.00'),
        'standard_charge|discounted_cash': Decimal('90.00'),
        'standard_charge|min': Decimal('70.00'),
        'standard_charge|max': Decimal('120.00')
    }
    fields['code|1'] = (str, None)
    fields['code|1|type'] = (str, None)
    if csv_type == CsvType.TALL:
        fields['payer_name'] = (str, None)
        fields['plan_name'] = (str, None)
        model_data.update({
            'payer_name': 'payer A',
            'plan_name': 'plan A1',
        })
    elif csv_type == CsvType.WIDE:
        fields['standard_charge|payer A|plan A1|negotiated_dollar'] = (Decimal, None)
        fields['standard_charge|payer A|plan A1|negotiated_percentage'] = (Decimal, None)
        fields['standard_charge|payer A|plan A1|negotiated_algorithm'] = (str, None)
        fields['estimated_amount|payer A|plan A1'] = (Decimal, None)
        fields['standard_charge|payer A|plan A1|methodology'] = (str, None)
        fields['additional_payer_notes|payer A|plan A1'] = (str, None)

        model_data.update({
            'standard_charge|payer A|plan A1|negotiated_dollar': Decimal('80.00'),
            'standard_charge|payer A|plan A1|negotiated_percentage': Decimal('80.00'),
            'standard_charge|payer A|plan A1|negotiated_algorithm': 'algorithm A',
            'estimated_amount|payer A|plan A1': Decimal('80.00'),
            'standard_charge|payer A|plan A1|methodology': 'fee schedule',
            'additional_payer_notes|payer A|plan A1': 'note A'
        })
    else:
        raise ValueError(f"CsvType({csv_type}) is not supporte.")
    return create_model('StandardChargeDynamicModel', **fields)(**model_data)
