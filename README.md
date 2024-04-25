# LDBack

npm install

Python 3.11 is needed

# start development instance

npx firebase emulators:start --only functions

# run unittests from funcions directory

cd functions
python -m pytest ./test/parser/test_docx_parser.py
