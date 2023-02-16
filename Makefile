# Install
init requirements.txt:
	pip install -r requirements.txt

# Compile
compile hunt-match-tracker.py:
	pyinstaller -F hunt-match-tracker.py

# Testing
test:
	pytest --cache-clear --durations=0 -v

# Launch Configs
launch: 
	./dist/hunt-match-tracker.exe

launch-help: 
	./dist/hunt-match-tracker.exe -h

launch-debug: 
	./dist/hunt-match-tracker.exe --debug=True