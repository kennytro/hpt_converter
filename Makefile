run-test:
	PYTHONPATH=$(PWD)/src pytest tests -s

.PHONY: run-test
