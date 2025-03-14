# Customization and Extension Guide

This document provides guidance on how to customize and extend the RAG application to meet specific requirements.

## Configuration Files

The application uses several configuration files that can be modified to customize its behavior:

### 1. Environment Variables (`.env`)

The `.env` file contains environment variables that control various aspects of the application. See the [Deployment Guide](./deployment-guide.md) for a complete list of environment variables.

### 2. Loader Configuration (`config/loaders.yaml`)

This file configures the document loaders used for ingesting data.

Example:
```yaml
file:
  use_llama_parse: false

web:
  driver_arguments:
    - "--headless"
    - "--disable-gpu"
  urls:
    - base_url: "https://example.com"
      prefix: "https://example.com"
      max_depth: 2

db:
  - uri: "sqlite:///example.db"
    queries:
      - "SELECT * FROM documents"
```

### 3. Tool Configuration (`config/tools.yaml`)

This file configures the tools available to the chat engine.

Example:
```yaml
local:
  duckduckgo:
    max_results: 5
  document_generator:
    default_type: "pdf"

llamahub:
  weather:
    api_key: "${WEATHER_API_KEY}"
  wikipedia.WikipediaToolSpec:
    top_k: 3
```

## Adding New Document Sources

### 1. Adding Local Documents

Simply add documents to the `data` directory. Supported file types include:
- PDF
- DOCX
- TXT
- HTML
- Markdown
- CSV
- JSON

After adding documents, run `poetry run generate` to process them.

### 2. Configuring Web Scraping

Edit the `config/loaders.yaml` file to add new websites:

```yaml
web:
  driver_arguments:
    - "--headless"
    - "--disable-gpu"
  urls:
    - base_url: "https://example.com"
      prefix: "https://example.com"
      max_depth: 2
```

### 3. Configuring Database Loaders

Edit the `config/loaders.yaml` file to add new database connections:

```yaml
db:
  - uri: "postgresql://user:password@localhost:5432/mydb"
    queries:
      - "SELECT title, content FROM articles"
```

## Customizing the Chat Engine

### 1. System Prompt

The system prompt controls the behavior of the chat engine. Edit the `SYSTEM_PROMPT` environment variable in the `.env` file:

```
SYSTEM_PROMPT="You are a helpful assistant who helps users with their questions.
You have access to a knowledge base including the facts that you should start with to find the answer for the user question. Use the query engine tool to retrieve the facts from the knowledge base.
..."
```

### 2. Next Question Suggestions

The next question suggestions feature can be customized by editing the `NEXT_QUESTION_PROMPT` environment variable in the `.env` file:

```
NEXT_QUESTION_PROMPT="You're a helpful assistant! Your task is to suggest the next question that user might ask. 
Here is the conversation history
---------------------
{conversation}
---------------------
..."
```

### 3. Conversation Starters

Conversation starters can be customized by editing the `CONVERSATION_STARTERS` environment variable in the `.env` file:

```
CONVERSATION_STARTERS=What standards for letters exist?
What are the requirements for a letter to be considered a letter?
```

## Adding New Tools

### 1. Tool Implementation

Create a new Python file in the `app/engine/tools` directory:

```python
# app/engine/tools/my_tool.py
from llama_index.core.tools.function_tool import FunctionTool

def my_function(parameter1: str, parameter2: int = 10):
    """
    Description of my function.
    
    Args:
        parameter1: Description of parameter1
        parameter2: Description of parameter2, default is 10
    
    Returns:
        Result of the function
    """
    # Implementation...
    return f"Processed {parameter1} with parameter2={parameter2}"

def get_tools(**kwargs):
    return [
        FunctionTool.from_defaults(my_function),
    ]
```

### 2. Tool Configuration

Add the tool to the `config/tools.yaml` file:

```yaml
local:
  my_tool:
    custom_param: "value"
```

### 3. Using LlamaHub Tools

LlamaHub tools can be configured in the `config/tools.yaml` file:

```yaml
llamahub:
  weather:
    api_key: "${WEATHER_API_KEY}"
  wikipedia.WikipediaToolSpec:
    top_k: 3
```

## Customizing Models

### 1. Changing LLM Provider

Edit the `MODEL_PROVIDER` environment variable in the `.env` file:

```
MODEL_PROVIDER=anthropic
MODEL=claude-3-opus
```

### 2. Changing Embedding Model

Edit the `EMBEDDING_MODEL` and `EMBEDDING_DIM` environment variables in the `.env` file:

```
EMBEDDING_MODEL=text-embedding-3-large
EMBEDDING_DIM=1024
```

### 3. Using Azure OpenAI

Edit the environment variables in the `.env` file:

```
MODEL_PROVIDER=azure-openai
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=your-azure-openai-endpoint
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_LLM_DEPLOYMENT=your-llm-deployment-name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment-name
```

## Extending the API

### 1. Adding New Endpoints

Create a new router file in the `app/api/routers` directory:

```python
# app/api/routers/my_endpoint.py
from fastapi import APIRouter

my_router = r = APIRouter()

@r.get("/my-endpoint")
def my_endpoint():
    return {"message": "Hello, world!"}
```

Add the router to the `app/api/routers/__init__.py` file:

```python
from .my_endpoint import my_router  # noqa: F401

api_router = APIRouter()
# ...
api_router.include_router(my_router, prefix="/my-endpoint")
```

### 2. Adding New Models

Create new data models in the `app/api/routers/models.py` file or in a new file:

```python
from pydantic import BaseModel

class MyModel(BaseModel):
    field1: str
    field2: int = 0
```

### 3. Adding New Services

Create a new service file in the `app/services` directory:

```python
# app/services/my_service.py
class MyService:
    @classmethod
    def my_method(cls, param):
        # Implementation...
        return result
```

## Customizing Frontend Integration

### 1. Configuring Frontend Endpoint

Edit the `FRONTEND_ENDPOINT` environment variable in the `.env` file:

```
FRONTEND_ENDPOINT=http://localhost:3000
```

### 2. Mounting Custom Static Files

Edit the `main.py` file to mount additional static files:

```python
mount_static_files("my_static_dir", "/api/files/my_static")
```

## Advanced Customization

### 1. Custom Document Loaders

Create a custom document loader in the `app/engine/loaders` directory:

```python
# app/engine/loaders/my_loader.py
from typing import List
from llama_index.core import Document
from pydantic import BaseModel

class MyLoaderConfig(BaseModel):
    param1: str
    param2: int = 0

def get_my_documents(config: MyLoaderConfig) -> List[Document]:
    # Implementation...
    return documents
```

Add the loader to the `app/engine/loaders/__init__.py` file:

```python
from .my_loader import MyLoaderConfig, get_my_documents

def get_documents() -> List[Document]:
    documents = []
    config = load_configs()
    for loader_type, loader_config in config.items():
        match loader_type:
            # ...
            case "my_loader":
                document = get_my_documents(MyLoaderConfig(**loader_config))
            # ...
        documents.extend(document)

    return documents
```

### 2. Custom Query Engines

Create a custom query engine in the `app/engine/tools` directory:

```python
# app/engine/tools/my_query_engine.py
from llama_index.core.base.base_query_engine import BaseQueryEngine

class MyQueryEngine(BaseQueryEngine):
    # Implementation...
    
    def _query(self, query_str):
        # Implementation...
        return response
        
    async def _aquery(self, query_str):
        # Implementation...
        return response
```

Use the custom query engine in the `app/engine/tools/query_engine.py` file:

```python
def create_query_engine(index, **kwargs) -> BaseQueryEngine:
    # ...
    if custom_condition:
        return MyQueryEngine(index, **kwargs)
    # ...
    return index.as_query_engine(**kwargs)
```

### 3. Custom Response Processing

Create a custom response processor in the `app/api/routers` directory:

```python
# app/api/routers/my_response.py
class MyResponse(StreamingResponse):
    # Implementation...
```

Use the custom response processor in the appropriate route handler:

```python
@r.post("/my-response")
async def my_response(request: Request, data: MyData):
    # ...
    return MyResponse(request, response)
```

## Performance Optimization

### 1. Optimizing Chunking Strategy

Edit the `CHUNK_SIZE` and `CHUNK_OVERLAP` environment variables in the `.env` file:

```
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### 2. Optimizing Embedding Dimensions

Edit the `EMBEDDING_DIM` environment variable in the `.env` file:

```
EMBEDDING_DIM=768
```

### 3. Optimizing Document Processing

Customize the document processing pipeline in the `app/engine/generate.py` file:

```python
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(
            chunk_size=Settings.chunk_size,
            chunk_overlap=Settings.chunk_overlap,
            separator="\n\n",  # Custom separator
        ),
        Settings.embed_model,
    ],
    docstore=docstore,
    docstore_strategy=DocstoreStrategy.UPSERTS_AND_DELETE,
    vector_store=vector_store,
)
```

## Testing Customizations

### 1. Testing API Endpoints

```bash
curl --location 'localhost:8000/api/my-endpoint'
```

### 2. Testing Document Processing

```bash
poetry run generate
```

### 3. Testing Chat Engine

```bash
curl --location 'localhost:8000/api/chat' \
--header 'Content-Type: application/json' \
--data '{ "messages": [{ "role": "user", "content": "Test message" }] }'
```
