# RAG Implementation Documentation

This document provides detailed information about the Retrieval-Augmented Generation (RAG) implementation in the application.

## Overview

Retrieval-Augmented Generation (RAG) is a technique that enhances Large Language Models (LLMs) by retrieving relevant information from a knowledge base and using that information to augment the model's responses. This approach combines the strengths of retrieval-based and generation-based methods to provide more accurate and contextually relevant answers.

In this application, RAG is implemented using:
- **llama-index**: For document processing, embedding, indexing, and retrieval
- **ChromaDB**: As the vector database for storing and retrieving document embeddings
- **Various LLM providers**: For generating responses (OpenAI, Anthropic, etc.)

## RAG Flow

The RAG implementation follows these steps:

1. **Document Ingestion**: Documents from various sources are processed, chunked, and embedded
2. **Indexing**: Embeddings are stored in ChromaDB for efficient retrieval
3. **Query Processing**: User queries are processed to retrieve relevant documents
4. **Response Generation**: Retrieved documents are used to augment LLM responses

## Document Ingestion

### Document Sources

Documents can be ingested from various sources:

1. **Files**: PDF, DOCX, TXT, and other file formats in the `data` directory
2. **Web Pages**: Websites and web content
3. **Databases**: Content from SQL databases

### Ingestion Pipeline

The ingestion pipeline is defined in `app/engine/generate.py`:

```python
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(
            chunk_size=Settings.chunk_size,
            chunk_overlap=Settings.chunk_overlap,
        ),
        Settings.embed_model,
    ],
    docstore=docstore,
    docstore_strategy=DocstoreStrategy.UPSERTS_AND_DELETE,
    vector_store=vector_store,
)
```

This pipeline:
1. Splits documents into sentences or chunks
2. Embeds the chunks using the configured embedding model
3. Stores the chunks and embeddings in the document store and vector store

### Configuration Parameters

Document processing can be configured with the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `CHUNK_SIZE` | Size of document chunks | 1024 |
| `CHUNK_OVERLAP` | Overlap between chunks | 20 |
| `EMBEDDING_MODEL` | Embedding model to use | text-embedding-3-large |
| `EMBEDDING_DIM` | Dimension of the embeddings | 1024 |

## Vector Database

The application uses ChromaDB as the vector database for storing and retrieving document embeddings.

### Configuration

ChromaDB can be configured in the following ways:

1. **Local ChromaDB**:
   ```
   CHROMA_PATH=/path/to/chroma.sqlite3
   CHROMA_COLLECTION=classroom
   ```

2. **Remote ChromaDB**:
   ```
   CHROMA_HOST=localhost
   CHROMA_PORT=8080
   CHROMA_COLLECTION=classroom
   ```

### Implementation

The ChromaDB integration is implemented in `app/engine/vectordb.py`:

```python
def get_vector_store():
    collection_name = os.getenv("CHROMA_COLLECTION", "default")
    chroma_path = os.getenv("CHROMA_PATH")
    
    if chroma_path:
        store = ChromaVectorStore.from_params(
            persist_dir=chroma_path, collection_name=collection_name
        )
    else:
        store = ChromaVectorStore.from_params(
            host=os.getenv("CHROMA_HOST"),
            port=os.getenv("CHROMA_PORT", "8001"),
            collection_name=collection_name,
        )
    return store
```

## Retrieval Process

### Query Engine

The query engine is responsible for retrieving relevant documents based on user queries. It is implemented in `app/engine/tools/query_engine.py`:

```python
def create_query_engine(index, **kwargs) -> BaseQueryEngine:
    top_k = int(os.getenv("TOP_K", 0))
    if top_k != 0 and kwargs.get("filters") is None:
        kwargs["similarity_top_k"] = top_k
    
    # Additional configuration...
    
    return index.as_query_engine(**kwargs)
```

### Query Filtering

The application supports filtering queries based on document properties, especially the public/private status of documents and specific document IDs. This is implemented in `app/engine/query_filter.py`:

```python
def generate_filters(doc_ids):
    public_doc_filter = MetadataFilter(
        key="private",
        value="true",
        operator="!=",
    )
    selected_doc_filter = MetadataFilter(
        key="doc_id",
        value=doc_ids,
        operator="in",
    )
    
    # Logic for combining filters...
    
    return filters
```

### Configuration Parameters

Retrieval can be configured with the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `TOP_K` | Number of similar embeddings to return | (varies) |

## Response Generation

### Chat Engine

The chat engine orchestrates the process of generating responses based on user queries and retrieved documents. It is implemented in `app/engine/engine.py`:

```python
def get_chat_engine(params=None, event_handlers=None, **kwargs):
    system_prompt = os.getenv("SYSTEM_PROMPT")
    tools: List[BaseTool] = []
    
    # Add query tool if index exists
    index_config = IndexConfig(callback_manager=callback_manager, **(params or {}))
    index = get_index(index_config)
    if index is not None:
        query_engine_tool = get_query_engine_tool(index, **kwargs)
        tools.append(query_engine_tool)
    
    # Add additional tools
    configured_tools: List[BaseTool] = ToolFactory.from_env()
    tools.extend(configured_tools)
    
    return AgentRunner.from_llm(
        llm=Settings.llm,
        tools=tools,
        system_prompt=system_prompt,
        callback_manager=callback_manager,
        verbose=True,
    )
```

### Multi-Modal Support

The application supports multi-modal responses if the configured LLM supports it. This is implemented in the `MultiModalSynthesizer` class in `app/engine/tools/query_engine.py`.

### System Prompts

The system prompt guides the behavior of the LLM and can be configured in the `.env` file:

```
SYSTEM_PROMPT="You are a helpful assistant who helps users with their questions.
You have access to a knowledge base including the facts that you should start with to find the answer for the user question. Use the query engine tool to retrieve the facts from the knowledge base.
You have access to the duckduckgo search tool. Use it to get information from the web to answer user questions.
For better results, you can specify the region parameter to get results from a specific region but it's optional.
If user request for a report or a post, use document generator tool to create a file and reply with the link to the file.
"
```

### Next Question Suggestions

The application can suggest follow-up questions based on the conversation history. This is configured using the `NEXT_QUESTION_PROMPT` environment variable.

## Tools Integration

The application integrates various tools that enhance the RAG capabilities:

### Query Engine Tool

The query engine tool is the primary tool for retrieving information from the knowledge base. It is implemented in `app/engine/tools/query_engine.py`.

### DuckDuckGo Search Tool

The DuckDuckGo search tool allows the assistant to search the web for information that may not be in the knowledge base. It is implemented in `app/engine/tools/duckduckgo.py`.

### Document Generator Tool

The document generator tool allows the assistant to create PDF and HTML documents. It is implemented in `app/engine/tools/document_generator.py`.

### Custom Tools

Additional tools can be configured through the `config/tools.yaml` file and implemented in the `app/engine/tools` directory.

## LLM Integration

The application supports various LLM providers through the settings module in `app/settings.py`:

- OpenAI
- Groq
- Ollama
- Anthropic
- Gemini
- Mistral
- Azure OpenAI
- Hugging Face
- T-Systems LLMHub

Each provider is initialized with the appropriate settings based on environment variables.

## Performance Considerations

### Chunking Strategy

The chunking strategy affects both the quality of retrieval and the performance of the system. Larger chunks provide more context but may reduce precision, while smaller chunks improve precision but may lack context.

### Embedding Dimensions

The dimension of the embeddings affects the quality of retrieval and the storage requirements. Higher dimensions generally lead to better quality but require more storage and computation.

### Similarity Metrics

The similarity metric used for retrieval affects the relevance of retrieved documents. The application uses the default similarity metric of the vector store, which is typically cosine similarity.

## Troubleshooting

### Common Issues

1. **No documents returned**: Check if documents are properly ingested and embedded in ChromaDB.
2. **Irrelevant documents returned**: Adjust the `TOP_K` parameter or refine the query filtering.
3. **Slow responses**: Consider optimizing the chunking strategy or reducing the embedding dimensions.

### Logs

ChromaDB logs are stored in `chroma.log` and can be useful for diagnosing issues with the vector database.

## Advanced Configuration

### Custom Loaders

Custom document loaders can be configured in the `config/loaders.yaml` file.

### Custom Tools

Custom tools can be configured in the `config/tools.yaml` file.

### Custom Embeddings

The application supports various embedding models that can be configured in the `.env` file.
