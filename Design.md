# Book City
==========================

## Overview
------------

The Book City application is designed to allow users to search for books by title using the OpenLibrary API. The results will be run through the OLLAMA Large Language Model (LLM) API to generate a summary of each book, and then displayed to the user in a web browser.  The user should be able to see more results as desired.

## Components

### Frontend

* Built with React for efficient rendering and data binding
* Includes a simple search form that submits the title of the book to the server and displays the LLM-produced summaries along with the cover of the book, if available.  UI is no-frills, since this is a POC, and time is of the essence.  In a fuller implementation, we'd hope to have things like autocomplete on the title, other books by the same author, and other sorts of related books available from each of the books shown in the results.

### Backend

* Built using Python and Flask for creating a RESTful API.  For a non-POC, it might make sense to use Django, but this is a very lightweight app that doesn't need all the frills offered by Django.
* Integrates with OpenLibrary API to retrieve book metadata and text summaries
* Utilizes Ollama, a local Large Language Model service (running llama-3.2), to generate text summaries for each book. In a production setting, this application would use an external LLM provider (e.g. Huggingface or Amazon Bedrock) or a internally-hosted version of the LLM, so it could be run on more appropriate hardware (and be scalable).  https://ollama.com/, https://github.com/ollama/ollama-python

## Flow

1. User submits a search query (book title) through the frontend application.
2. Frontend sends request to Flask with search query, which routes the query to the Search API.
4. The search API retrieves book metadata from the OpenLibrary API using the provided title, then returns that to the UI for immediate rendering.
5. The UI requests from the backend an enriched version of the record for the book.
5. The book API passes the ISBN numbers to the OpenLibrary Book service to find the URL for the book cover, and simultaneously passes the entire JSON result from the OpenLibrary API to Ollama to process each of the search results and generate text summaries of each book.
6. The book API combines the text summaries with the cover URL and original JSON from the search service to the frontend application in JSON. 
7. Frontend displays the entire record to the user, including the cover image and the LLM-generated summary.  

## Tradeoffs

* While it's cleanest to get all the data for a book (including the summary) and send it back as a single JSON object, that will likely cause too much latency, since LLMs are relatively slow (as is the service to find the book covers).  Thus, it might make mores sense to send back the straightforward data immediately, and then either generate the summary in a subsequent call.  In a non-POC, it would make sense to use a websocket to send the data back as it becomes available rather than using a 1+n fetch model to get the more expensive data.  Similarly, it would make sense to pre-fetch at least some of the data for the next page of results, assuming sufficient server capacity and click-throughs to the next page of results.

* In a real application, using an LLM to generate the entire summary of the data from the OpenLibrary API result seems like the wrong approach.  Since there's already lots of structured data that could easily be displayed, it would probably be more useful to the user to simply display the structured data rather than an LLM-generated summary of that data.

* The resulting application is limited in its utility, since there are no links to actually get/use the book.  In a real application, there would be some additional actions that could be carried out on the results of the search, but that's beyond the scope of the current request.

* The use of the Ollama library makes the project fairly portable, without the need to have any API keys that would need to be supplied by anyone testing out the app.  The use of the relatively small Llama-3.2 model allows the application to be run on a standard desktop machine.

## Database Schema

The application does not require a traditional database schema, as it only processes search query metadata and temporary results from the LLM integration.

However, for future development, it might make sense to include a caching layer, such as a REDIS cache, to store the LLM-generated summaries.

## Security Considerations

* User authentication: Implement a simple login system to ensure only authorized users can access the application.  Not implemented for this POC.
* Data encryption: Use HTTPS to encrypt data in transit and protect sensitive information (e.g. book titles, search queries).  Not implemented for this POC.
* API key management: None required for this version.  If a hosted LLM was used (or a different book service), it would be necessary to securely store and manage relevant credentials (e.g. API keys, other API credentials, security certificates)

## Technical Requirements

* Python 3.12
* Flask for backend API
* React and MobX for frontend framework
* Ollama installed locally

## Development Roadmap

1. Complete Frontend application with search form and display results in web browser
2. Implement Backend API with OpenLibrary API integration and LLM integration using Ollama
3. Conduct thorough testing and debugging of the entire application
4. Future: Add automated tests and develop additional features, such as user authentication and data encryption, as well as whatever the real application should be.

