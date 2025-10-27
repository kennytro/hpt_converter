
# Abstract Schema
Data in HPT file is split into 3 files:
* General data element
* Payer plan
* Standard charge

[NOTE]: Auto generate document. Do NOT manually edit this file.


# GeneralDataElements

|Name|Type|Description|
|---|:---:|---|
|file_id|String|The file identifier for the hospital price transparency file.|
|hospital_name|String|The legal business name of the licensee.|
|last_updated_on|String|Date on which the MRF was last updated. Date must be in an ISO 8601 format (i.e. YYYY-MM-DD).|
|version|String|The version of the CMS Template used.|
|hospital_location|String|The unique name of the hospital location absent any acronyms.|
|hospital_address|String|The geographic address of the corresponding hospital location.|
|license_number|Tuple[String, String]|The hospital license number and the licensing state or territory’s two-letter abbreviation for the hospital location(s) indicated in the file.|
|affirmation_statement|Boolean|Required affirmation statement.|
|financial_aid_policy|String|The hospital’s financial aid policy.|
|general_contract_provisions|String|Payer contract provisions that are negotiated at an aggregate level across items and services (e.g., claim level).|

# PayerPlan

|Name|Type|Description|
|---|:---:|---|
|file_id|String|The file identifier for the hospital price transparency file.|
|plan_id|String|The unique identifier for the payer’s specific plan associated with the standard charge.|
|payer_name|String|The name of the payer associated with the negotiated charge for the item or service.|
|plan_name|String|The name of the payer’s specific plan associated with the standard charge.|

# StandardCharge

|Name|Type|Description|
|---|:---:|---|
|file_id|String|The file identifier for the hospital price transparency file.|
|description|String|Description of each item or service provided by the hospital that corresponds to the standard charge the hospital has established.|
|codes|List[CodeInformation]|Any code(s) and type(s) used by the hospital for purposes of billing or accounting for the item or service. .|
|setting|Setting|Indicates whether the item or service is provided in connection with an inpatient admission or an outpatient department visit. |
|drug_unit_of_measurement|String|If the item or service is a drug, indicate the unit value that corresponds to the established standard charge..|
|drug_type_of_measurement|DrugTypeOfMeasument|The measurement type that corresponds to the established standard charge for drugs as defined by either the National Drug Code or the National Council for Prescription Drug Programs. |
|gross_charge|Decimal|Gross charge is the charge for an individual item or service that is reflected on a hospital’s chargemaster, absent any discounts.|
|discounted_cash|Decimal|The discounted cash price for the item or service.|
|plan_id|String|The unique identifier for the payer’s specific plan associated with the negotiated charge.|
|modifiers|String|Include any modifier(s) that may change the standard charge that corresponds to hospital items or services.|
|negotiated_dollar|Decimal|Payer-specific negotiated charge (expressed as a dollar amount) that a hospital has negotiated with a third-party payer for the corresponding item or service.|
|negotiated_percentage|Decimal|Payer-specific negotiated charge (expressed as a percentage) that a hospital has negotiated with a third-party payer for an item or service.|
|negotiated_algorithm|String|Payer-specific negotiated charge (expressed as an algorithm) that a hospital has negotiated with a third-party payer for the corresponding item or service.|
|estimated_amount|Decimal|Estimated allowed amount means the average dollar amount that the hospital has historically received from a third party payer for an item or service. If the standard charge is based on a percentage or algorithm, the MRF must also specify the estimated allowed amount for that item or service.|
|min_charge|Decimal|De-identified minimum negotiated charge is the lowest charge that a hospital has negotiated with all third-party payers for an item or service. This is determined from the set of negotiated standard charge dollar amounts.|
|max_charge|Decimal|De-identified maximum negotiated charge is the lowest charge that a hospital has negotiated with all third-party payers for an item or service. This is determined from the set of negotiated standard charge dollar amounts.|
|methodology|StandardChargeMethod|Method used to establish the payer-specific negotiated charge. The valid value corresponds to the contract arrangement.|
|additional_generic_notes|String|A free text data element that is used to help explain any of the data including, for example, blanks due to no applicable data, charity care policies, or other contextual information that aids in the public’s understanding of the standard charges.|
|additional_payer_notes|String|A free text data element used to help explain data in the file that is related to a payer-specific negotiated charge.|
