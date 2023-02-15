init requirements.txt:
	pip install -r requirements.txt

compile hunt-match-tracker.py:
	pyinstaller -F hunt-match-tracker.py

test:
	pytest
