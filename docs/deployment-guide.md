# Deployment Guide

This document provides detailed instructions for deploying the RAG application to various environments.

## Prerequisites

Before deploying the application, ensure you have the following:

1. Python 3.11 or later installed
2. Poetry for dependency management
3. Environment variables configured in `.env` file
4. Documents in the `data` directory (if needed)

## Local Development Deployment

### 1. Install Dependencies

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with the necessary configuration:

```
# Required variables
MODEL_PROVIDER=openai
MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=1024
OPENAI_API_KEY=your_openai_api_key

# ChromaDB configuration
CHROMA_COLLECTION=classroom
CHROMA_HOST=localhost
CHROMA_PORT=8080

# Application configuration
APP_HOST=0.0.0.0
APP_PORT=8000
```

See the `.env` file for all available configuration options.

### 3. Generate Embeddings

Generate embeddings for the documents in the `data` directory:

```bash
poetry run generate
```

### 4. Start Development Server

```bash
poetry run dev
```

This will start the application on `http://localhost:8000`.

## Production Deployment

### 1. Build Frontend (if included)

```bash
poetry run build
```

### 2. Start Production Server

```bash
poetry run prod
```

## Docker Deployment

### 1. Build Docker Image

```bash
docker build -t rag-application .
```

### 2. Run Docker Container

```bash
docker run \
  -v $(pwd)/.env:/app/.env \ # Use ENV variables and configuration from your file-system
  -v $(pwd)/config:/app/config \
  -v $(pwd)/storage:/app/storage \ # Use your file system to store vector embeddings
  -p 8000:8000 \
  rag-application
```

### 3. Generate Embeddings in Docker

If you're having documents in the `./data` folder, run the following command to generate vector embeddings:

```bash
docker run \
  --rm \
  -v $(pwd)/.env:/app/.env \ # Use ENV variables and configuration from your file-system
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \ # Use your local folder to read the data
  -v $(pwd)/storage:/app/storage \ # Use your file system to store the vector database
  rag-application \
  poetry run generate
```

## Fly.io Deployment

### 1. Install Fly CLI

Install the Fly.io CLI according to the [official documentation](https://fly.io/docs/flyctl/install/).

### 2. Authenticate with Fly.io

```bash
fly auth login
```

### 3. Launch Application

```bash
fly launch
```

Follow the prompts to configure your application.

### 4. Open Application

```bash
fly apps open
```

### 5. Generate Embeddings on Fly.io

If you're having documents in the `./data` folder, run the following command to generate vector embeddings:

```bash
fly console --machine <machine_id> --command "poetry run generate"
```

Where `machine_id` is the ID of the machine where the app is running. You can show the running machines with the `fly machines` command.

> **Note**: Using documents will make the app stateful. As Fly.io is a stateless app, you should use [LlamaCloud](https://docs.cloud.llamaindex.ai/llamacloud/getting_started) or a vector database to store the embeddings of the documents. This applies also for document uploads by the user.

## Environment Variables

Here's a complete list of environment variables that can be configured:

### Model Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_PROVIDER` | Provider for AI models (openai, groq, ollama, anthropic, gemini, mistral, azure-openai, huggingface, t-systems) | openai |
| `MODEL` | Name of the LLM model to use | gpt-4o-mini |
| `EMBEDDING_MODEL` | Name of the embedding model to use | text-embedding-3-large |
| `EMBEDDING_DIM` | Dimension of the embedding model | 1024 |
| `LLM_TEMPERATURE` | Temperature for sampling from the model | (provider default) |
| `LLM_MAX_TOKENS` | Maximum number of tokens to generate | (provider default) |

### API Keys

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `LLAMA_CLOUD_API_KEY` | Llama Cloud API key |
| (Various provider-specific API keys) | Check settings.py for details |

### ChromaDB Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMA_COLLECTION` | Name of the collection in ChromaDB | classroom |
| `CHROMA_HOST` | Hostname for ChromaDB | localhost |
| `CHROMA_PORT` | Port for ChromaDB | 8080 |
| `CHROMA_PATH` | Local path to ChromaDB | (none) |

### Application Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_HOST` | Address to start the backend app | 0.0.0.0 |
| `APP_PORT` | Port to start the backend app | 8000 |
| `FILESERVER_URL_PREFIX` | URL prefix of the server storing the images | http://localhost:8000/api/files |
| `FRONTEND_ENDPOINT` | Frontend endpoint for development | (none) |
| `ENVIRONMENT` | Environment (dev or prod) | dev |

### Prompts and Behavior

| Variable | Description |
|----------|-------------|
| `SYSTEM_PROMPT` | System prompt for the AI model |
| `NEXT_QUESTION_PROMPT` | Prompt to generate next question suggestions |
| `CONVERSATION_STARTERS` | Questions to help users get started |

### RAG Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TOP_K` | Number of similar embeddings to return | (varies) |
| `CHUNK_SIZE` | Size of document chunks | 1024 |
| `CHUNK_OVERLAP` | Overlap between document chunks | 20 |

## Persistence Considerations

### Storage Strategy

The application uses several types of storage:

1. **Vector Database**: ChromaDB for storing document embeddings
2. **Document Store**: For storing document content and metadata
3. **File Storage**: For storing uploaded files and generated documents

For stateless deployments (like Fly.io), consider using external services for persistence:

1. **Remote ChromaDB**: Configure using `CHROMA_HOST` and `CHROMA_PORT`
2. **LlamaCloud**: Configure using `LLAMA_CLOUD_API_KEY`
3. **Cloud Storage**: For file storage

### Backup and Recovery

To backup the application state:

1. Copy the `storage` directory
2. Copy the ChromaDB data (`my_chroma_data` or the configured `CHROMA_PATH`)
3. Copy the `data` directory for original documents

## Troubleshooting Deployments

### Common Issues

1. **Application won't start**: Check error logs and ensure all dependencies are installed
2. **ChromaDB connection error**: Verify ChromaDB is running and accessible
3. **API key issues**: Ensure all necessary API keys are configured
4. **Vector store not loading**: Check ChromaDB logs and configuration

### Logs

Check the following logs for debugging:

1. Application logs from the server
2. ChromaDB logs in `chroma.log`
3. Docker logs if using Docker deployment
4. Fly.io logs if using Fly.io deployment (`fly logs`)

## Security Considerations

1. **API Keys**: Store API keys securely, especially in production environments
2. **Document Access**: Configure appropriate access controls for documents
3. **Network Security**: Configure CORS and other network security measures
4. **Environment Variables**: Use environment-specific configurations

## Performance Optimization

1. **Vector Store**: Use a properly sized ChromaDB instance
2. **Embedding Model**: Choose an embedding model with appropriate performance characteristics
3. **LLM Model**: Select an LLM with the right balance of quality and performance
4. **Resource Allocation**: Allocate appropriate resources to the application
