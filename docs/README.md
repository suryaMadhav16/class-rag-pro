# RAG Application Backend Documentation

This documentation provides an overview and detailed analysis of the Retrieval-Augmented Generation (RAG) application backend that uses llama-index and ChromaDB.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Key Components](#key-components)
4. [Setup and Configuration](#setup-and-configuration)
5. [Deployment Options](#deployment-options)
6. [API Endpoints](#api-endpoints)
7. [Features](#features)
8. [Development Workflow](#development-workflow)

## System Overview

This is a chat application backend that implements Retrieval-Augmented Generation (RAG) using llama-index and ChromaDB. The application enhances standard LLM capabilities by retrieving relevant information from a knowledge base to provide more accurate and contextual responses.

The system is built with FastAPI and supports both streaming and non-streaming chat interfaces. It includes various tools for document search, web search, document generation, and other functionalities that can be configured through configuration files.

## Architecture

The application follows a layered architecture:

1. **API Layer** - Handles HTTP requests and responses, implements endpoints for chat, file upload, etc.
2. **Engine Layer** - Core RAG implementation, manages the index, vector store, and query engines
3. **Services Layer** - Provides utilities for file handling, suggestions, etc.
4. **Infrastructure Layer** - Handles database connections, file storage, etc.

### Data Flow

1. Documents are loaded from various sources (files, web, databases)
2. Documents are chunked, embedded, and stored in ChromaDB
3. User queries are processed by retrieving relevant documents
4. Retrieved content is used to augment LLM responses
5. The enhanced response is returned to the user

## Key Components

### 1. Document Processing and Embedding

The application can ingest documents from various sources:
- Local files (PDF, DOCX, TXT, etc.)
- Web pages
- Database content

Documents are chunked into smaller pieces, embedded using an embedding model (configured in settings), and stored in ChromaDB.

### 2. Chat Engine

The chat engine combines the power of LLMs with the knowledge base. It uses:
- Agent-based approach with tools
- Query engine for retrieving relevant information
- Custom system prompts

### 3. Tools

The application includes various tools that enhance the chat experience:
- Query engine tool for retrieving information
- DuckDuckGo search tool for web searches
- Document generator tool for creating PDF and HTML documents
- Various other tools that can be configured

### 4. API Endpoints

The application provides several endpoints:
- Streaming and non-streaming chat
- Configuration endpoints
- File upload
- Direct query

## Setup and Configuration

### Environment Variables

The application is configured through environment variables defined in the `.env` file:

- Model provider and model configuration
- Embedding model settings
- ChromaDB configuration
- System prompts and custom prompts
- Application host and port settings

### Configuration Files

Additional configuration is provided through YAML files in the `config` directory:
- `loaders.yaml` - Configuration for document loaders
- `tools.yaml` - Configuration for tools

## Deployment Options

The application supports various deployment options:

### Local Development

```bash
poetry install
poetry shell
poetry run generate  # Generate embeddings for documents
poetry run dev       # Start development server
```

### Docker Deployment

```bash
docker build -t <your_image_name> .
docker run -v $(pwd)/.env:/app/.env -v $(pwd)/config:/app/config -v $(pwd)/storage:/app/storage -p 8000:8000 <your_image_name>
```

### Fly.io Deployment

```bash
fly auth login
fly launch
fly apps open
```

## API Endpoints

### Chat Endpoints

- `POST /api/chat` - Streaming chat endpoint
- `POST /api/chat/request` - Non-streaming chat endpoint

### Configuration Endpoints

- `GET /api/chat/config` - Get chat configuration (starter questions)
- `GET /api/chat/config/llamacloud` - Get LlamaCloud configuration (if enabled)

### File Upload Endpoint

- `POST /api/chat/upload` - Upload files for chat

### Query Endpoint

- `GET /api/query` - Direct query to the knowledge base

## Features

### Core Features

- **RAG Implementation** - Enhances LLM responses with retrieved information
- **Multi-modal Support** - Can process and respond to both text and image inputs (if configured)
- **Document Processing** - Can process various document types
- **Web Search Integration** - Can search the web for additional information
- **Document Generation** - Can generate PDF and HTML documents
- **Source Citation** - Provides sources for the information
- **Follow-up Questions** - Suggests follow-up questions

### Advanced Features

- **Streaming Responses** - Supports streaming responses for better user experience
- **Multiple Model Providers** - Supports various LLM providers
- **Custom System Prompts** - Configurable system prompts
- **Tool Integration** - Extensible tool framework

## Development Workflow

1. **Setup Environment** - Install dependencies and configure environment variables
2. **Add Documents** - Add documents to the `data` directory
3. **Generate Embeddings** - Run `poetry run generate` to create embeddings
4. **Start Development Server** - Run `poetry run dev` to start the server
5. **Test Endpoints** - Use the API documentation at `/docs` to test endpoints
6. **Deploy** - Deploy using Docker or Fly.io
