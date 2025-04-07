To run the FASTAPI server to access the book services:

Ensure that the environment var `OPENAI_API_KEY` is set via something like

```
export OPENAI_API_KEY="MY_KEY_GOES_HERE"
```

Working from the directory where this file is located:

    # If you haven't already created a venv for this:
    python -m venv .
    pip install -r requirements.txt

    * Or, if you already have a venv for this project:
    ./venv/bin/activate

    # in either case, get it running
    fastapi dev main.py

Go here to test it out

    http://127.0.0.1:8000

### Using llama instead of OpenAI

Note that if you want to run with llama-3.2, you need to do the following as well:

Make sure ollama is running. Install from https://ollama.com/download and then call

    ollama pull llama3.2
    ollama serve

edit `main.py` to include llama-3.2 and exclude gpt-4o-mini from this

```
class Settings(BaseSettings):
    books_per_page: int = 10
    model: str = 'gpt-4o-mini'
#    model: str = 'llama3.2'
```

to this

```
class Settings(BaseSettings):
    books_per_page: int = 10
#    model: str = 'gpt-4o-mini'
    model: str = 'llama3.2'
```
