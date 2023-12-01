.PHONY: test clean

test:
	python3 -m doctest db_utils.py
	python3 -m doctest log_parser.py
	python3 -m doctest op_log.py
	python3 -m doctest trace_translator.py

clean:
	rm -rf ./__pycache__
	rm -rf *.log
	rm -rf *.pkl