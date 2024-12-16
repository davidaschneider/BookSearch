To run the FLASK server to access the book services

Make sure ollama is running.  Install from https://ollama.com/download and then call

    ollama pull llama3.2
    ollama serve

Working from the directory where this file is located:

    source ./venv/bin/activate
    pip install flask aiohttp flask_mail requests ollama

    export FLASK_DEBUG=1        # OPTIONAL adds debugging into the flask logs
    flask run --port 5000


To run interactively for testing:

    flask shell
    from app.book import *






