# LDBack
```bash
npm install
```
Python 3.11 is needed
```bash
.\venv\scripts\activate.ps1
```
```bash
pip install -r .\requirements.txt
```
pip install -r .\requirements.txt
```bash
pip freeze > .\requirements.txt
```
# start development instance
```bash
npx firebase emulators:start --only functions


# run unittests from funcions directory

cd functions
python -m pytest ./test/parser/test_docx_parser.py
python -m pytest ./test/

# run with docker 

cd docker 
docker compose up
=======
```
```bash
python dev_app.py  
```
# run unittests from root directory
```bash
python -m unittest
```
```bash
python -m pytest ./test
```
