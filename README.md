# LDBack

npm install

Python 3.11 is needed

python -m venv
pip install -r .\requirements.txt

# start development instance

npx firebase emulators:start --only functions
python dev_app.py  

# run unittests from root directory

python -m unittest
python -m pytest ./test

