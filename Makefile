run-test:
	PYTHONPATH=$(PWD)/src pytest tests -s

schema-readme:
	PYTHONPATH=$(PWD)/src python src/tools/make_schema_readme.py

# to upgrade the JSON schema version(currently v2), update the variables below.
json-schema: URL = https://raw.githubusercontent.com/CMSgov/hospital-price-transparency/refs/heads/master/documentation/JSON/schemas/V2.2.1_Hospital_price_transparency_schema.json
json-schema: OUTPUT = $(PWD)/src/hpt_converter/lib/schema/json/v2/hpt.py
json-schema:
	datamodel-codegen --url $(URL) --output $(OUTPUT) --input-file-type jsonschema \
	--class-name HospitaPriceTransparency \
	--output-model-type="pydantic_v2.BaseModel" \
	--use-annotated

.PHONY: run-test schema-readme json-schema
