# Use a Linux-based Python image
FROM python:3.10-slim

WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl

COPY dist/llmchat-0.1.0-py3-none-any.whl /app/llmchat-0.1.0-py3-none-any.whl

RUN pip install --no-cache-dir /app/llmchat-0.1.0-py3-none-any.whl

EXPOSE 5000

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "src.app:app"]