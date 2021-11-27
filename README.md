# state-bot

## Setup

### Virtual environment

```shell
$ virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

### Env config
Create `.env` file and set `API_TOKEN` with your token
```dotenv
API_TOKEN = "1111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
```

## Run tests

```shell
$ python -m pytest tests.py
```
