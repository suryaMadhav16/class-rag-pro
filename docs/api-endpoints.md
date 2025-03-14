# API Endpoints Documentation

This document provides detailed information about the API endpoints available in the application.

## Base URL

All endpoints are prefixed with `/api`.

## Chat Endpoints

### POST `/api/chat`

Streaming chat endpoint that allows real-time responses.

#### Request Body

```json
{
  "messages": [
    {
      "role": "user",
      "content": "What standards for letters exist?",
      "annotations": [
        {
          "type": "document_file",
          "data": {
            "files": [
              {
                "content": "data:text/plain;base64,aGVsbG8gd29ybGQK=",
                "name": "example.txt"
              }
            ]
          }
        }
      ]
    }
  ],
  "data": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `messages` | array | List of chat messages |
| `messages[].role` | string | Role of the message sender (`user` or `assistant`) |
| `messages[].content` | string | Content of the message |
| `messages[].annotations` | array | Optional annotations for the message |
| `data` | object | Optional additional data for the chat engine |

#### Response

Streaming response with the following format:

```
0:"token"
8:[{"type":"events","data":{"title":"Retrieving context for query: 'What standards for letters exist?'"}}]
8:[{"type":"sources","data":{"nodes":[...]}}]
0:"I'll "
0:"provide "
...
```

The response is streamed in chunks with:
- `0:` prefix for text tokens
- `8:` prefix for data events
- `3:` prefix for errors

### POST `/api/chat/request`

Non-streaming chat endpoint.

#### Request Body

Same as the streaming endpoint.

#### Response

```json
{
  "result": {
    "role": "assistant",
    "content": "Here's information about letter standards...",
    "annotations": null
  },
  "nodes": [
    {
      "id": "doc1",
      "metadata": {
        "file_name": "standards.pdf",
        "page": 1
      },
      "score": 0.92,
      "text": "Letter standards include...",
      "url": "http://localhost:8000/api/files/data/standards.pdf"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `result` | object | The assistant's response |
| `result.role` | string | Always "assistant" |
| `result.content` | string | Content of the response |
| `nodes` | array | Source nodes used to generate the response |
| `nodes[].id` | string | ID of the source node |
| `nodes[].metadata` | object | Metadata about the source |
| `nodes[].score` | number | Relevance score (0-1) |
| `nodes[].text` | string | Text content of the source |
| `nodes[].url` | string | URL to the source document if available |

## Chat Configuration Endpoints

### GET `/api/chat/config`

Returns configuration information for the chat interface.

#### Response

```json
{
  "starterQuestions": [
    "What standards for letters exist?",
    "What are the requirements for a letter to be considered a letter?"
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `starterQuestions` | array | List of starter questions for the chat interface |

### GET `/api/chat/config/llamacloud`

Returns LlamaCloud configuration if enabled.

#### Response

```json
{
  "projects": [
    {
      "project": "project1",
      "pipelines": ["pipeline1", "pipeline2"]
    }
  ],
  "pipeline": {
    "pipeline": "pipeline1",
    "project": "project1"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `projects` | array | List of available LlamaCloud projects and pipelines |
| `pipeline` | object | Currently configured pipeline |

## File Upload Endpoint

### POST `/api/chat/upload`

Uploads a file for use in chat.

#### Request Body

```json
{
  "base64": "data:text/plain;base64,aGVsbG8gd29ybGQK",
  "name": "example.txt",
  "params": {}
}
```

| Field | Type | Description |
|-------|------|-------------|
| `base64` | string | Base64-encoded file content |
| `name` | string | Name of the file |
| `params` | object | Optional parameters for file processing |

#### Response

```json
{
  "content": "data:text/plain;base64,aGVsbG8gd29ybGQK",
  "name": "example.txt",
  "refs": ["doc1", "doc2"]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Base64-encoded file content |
| `name` | string | Name of the file |
| `refs` | array | References to document IDs in the vector store |

## Query Endpoint

### GET `/api/query`

Directly queries the knowledge base without chat context.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | The query to search in the knowledge base |

#### Response

```
Text response containing the information from the knowledge base.
```

## Error Handling

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid request payload"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Error in chat engine: [error message]"
}
```

## Example Requests

### Example: Chat Request

```bash
curl --location 'localhost:8000/api/chat' \
--header 'Content-Type: application/json' \
--data '{ "messages": [{ "role": "user", "content": "Hello" }] }'
```

### Example: Non-Streaming Chat Request

```bash
curl --location 'localhost:8000/api/chat/request' \
--header 'Content-Type: application/json' \
--data '{ "messages": [{ "role": "user", "content": "Hello" }] }'
```

### Example: Query Request

```bash
curl --location 'localhost:8000/api/query?query=What%20are%20letter%20standards'
```

### Example: File Upload

```bash
curl --location 'localhost:8000/api/chat/upload' \
--header 'Content-Type: application/json' \
--data '{
  "base64": "data:text/plain;base64,SGVsbG8gd29ybGQ=",
  "name": "example.txt"
}'
```
