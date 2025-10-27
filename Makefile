run-test:
	PYTHONPATH=$(PWD)/src pytest tests -s

schema-readme:
	PYTHONPATH=$(PWD)/src python src/tools/make_schema_readme.py

.PHONY: run-test schema-readme
