import os

if os.path.exists('medium.secret'):
    # key exists
    with open('medium.secret') as f: key = f.read().strip()
    