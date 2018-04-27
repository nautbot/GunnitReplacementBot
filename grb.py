import subprocess, traceback

while True:
    try:
        p = subprocess.call(['python3', 'grbloop.py'])
    except (SyntaxError, FileNotFoundError):
        p = subprocess.call(['python', 'grbloop.py'])
    except:
        traceback.print_exc()
        pass