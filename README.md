# llm-local-chat
A simple chat application using Lang-Chain and RAG approach using llama3 

## Ollama setup and Installation
```bash
download and install : https://ollama.com/download
```
## Pull llama3 and paraphrase-multilingual model
```bash 
ollama pull llama3
ollama pull paraphrase-multilingual-MiniLM-L12-v2
```
## To install all required dependencies
```bash
pip install -r requirements.txt
```
## To refresh the app with new dependencies
```bash
poetry lock
poetry update
poetry sync
```
Update the poetry.lock and pyproject.toml files to include any other dependencies if needed

## To build
```bash 
poetry build
```
## To run the application locally using waitress after installing whl file
```bash
waitress-serve --port=5000 llmchat.app:app
```

## To run the application from an IDE
```bash 
app.py
```

This project as a docker file and kubernetes pod yml file to containerize and deploy the application in kubernetes cluster

Once the application is up and running, access localhost:5000/ui/upload in your browser to upload pdf files to store them in Vector DB. The content of the pdf file will be the context to LLM model.
Access localhost:5000/ to chat with the bot using the context from the pdf file.
