To run the FLASK server to access the book services

Make sure ollama is running.  Install from https://ollama.com/download and then call

    ollama pull llama3.2
    ollama serve

Working from the directory where this file is located:

    source ./venv/bin/activate
    pip install "fastapi[standard]" aiohttp requests ollama

    fastapi dev main.py

Go here to test it out

    http://127.0.0.1:8000 






