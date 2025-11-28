# Knowledge Base Assistant

An intelligent knowledge management system with document processing, semantic search, and AI-powered chat capabilities. Built with FastAPI, PostgreSQL, Qdrant vector database, and React frontend.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/fastapi-latest-brightgreen)
![License](https://img.shields.io/github/license/your-username/knowledge-base-assistant)

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Extending the System](#extending-the-system)
- [License](#license)

## Features

- **User Management**: Registration, authentication with JWT tokens, and role-based access control (RBAC)
- **Document Processing**: Upload and parse DOCX and Excel files with automatic content extraction
- **Knowledge Storage**: Store processed documents in PostgreSQL and MinIO object storage
- **Semantic Search**: Vectorize text content using embedding models and perform similarity searches with Qdrant
- **AI-Powered Chat**: Interactive chat interface with context-aware responses based on your knowledge base
- **Conversation History**: Persistent chat history tracking per user session

## Architecture

```
┌─────────────┐    HTTP    ┌──────────────┐
│   Frontend  ├───────────►│   FastAPI    │
│   (React)   │            │   Backend    │
└─────────────┘            └──────┬───────┘
                                  │
                       ┌──────────▼──────────┐
                       │ Business Logic &    │
                       │ Core Services       │
                       └──┬─────────┬────────┘
                          │         │
                ┌─────────▼─┐     ┌─▼──────────┐
                │           │     │            │
                │  Qdrant   │     │ PostgreSQL │
                │ Vector DB │     │     DB     │
                │           │     │            │
                └───────────┘     └────────────┘

                   ┌─────────────────┐
                   │   MinIO         │
                   │ Object Storage  │
                   └─────────────────┘
```

## Tech Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Database**: Qdrant
- **Object Storage**: MinIO
- **Authentication**: JWT tokens
- **Document Processing**: Mammoth (DOCX), Pandas (Excel)
- **Text Chunking**: Chonkie
- **Embeddings**: OpenAI Compatible API

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **Build Tool**: Vite

## Prerequisites

- Python 3.8+
- Node.js 14+
- PostgreSQL database
- MinIO object storage
- Qdrant vector database
- OpenAI-compatible API key (for embeddings and chat)
- [uv](https://github.com/astral-sh/uv) - Python package installer and resolver

## Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd knowledge-base-assistant
   ```

2. Create and activate a virtual environment with uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies using uv sync:
   ```bash
   uv sync
   ```

4. Set up environment variables (see [Configuration](#configuration))

5. Initialize the database:
   ```bash
   python -c "from app.core.init_db import init_db; init_db()"
   ```

6. Start the backend server:
   ```bash
   chmod +x start_fastapi.sh
   ./start_fastapi.sh
   ```
   
   Or directly:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8010 --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:3000.

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_DATABASE=knowledge_base

# MinIO Configuration
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=knowledge-files
MINIO_SECURE=False

# OpenAI Configuration (for chat)
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# Embedding Model Configuration
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_MODEL_NAME=text-embedding-ada-002
EMBEDDING_DIM=1536

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=knowledge_collection
VECTOR_SIZE=1536
```

## Usage

1. Register a new user account or log in with existing credentials
2. Upload documents (DOCX or Excel files) through the file upload interface
3. Wait for document processing to complete (documents are parsed, chunked, and vectorized)
4. Use the chat interface to ask questions about your uploaded documents
5. View conversation history in the chat interface

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8010/docs
- ReDoc: http://localhost:8010/redoc

Key API endpoints:
- `POST /register` - User registration
- `POST /login` - User login (returns JWT token)
- `POST /files/upload` - Upload document files
- `POST /chat/completions` - Chat with the knowledge base

## Project Structure

```
knowledge-base-assistant/
├── app/                    # Backend application
│   ├── api/               # API routes
│   ├── core/              # Core components (database, processors)
│   ├── dependencies/      # Dependency injection
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── services/      # API service layer
│   │   └── ...
│   └── ...
├── .env                   # Environment variables
├── start_fastapi.sh       # Backend startup script
└── pyproject.toml         # Python project configuration
```

## Database Schema

- **Users**: User accounts with authentication details
- **Roles**: User roles for access control
- **Permissions**: Available permissions in the system
- **Role-Permission**: Many-to-many relationship between roles and permissions
- **Knowledge Items**: Processed knowledge content from documents
- **Files**: Metadata for uploaded files
- **Chat Histories**: Conversation records with questions and answers

Vector embeddings are stored in Qdrant vector database for semantic search capabilities.

## Extending the System

Potential enhancements:
1. Support for additional document formats (PDF, TXT, etc.)
2. Web crawling capabilities for processing online content
3. Tagging system for organizing knowledge items
4. Sharing functionality with public/private access controls
5. Real-time progress notifications via WebSocket
6. Advanced analytics dashboard

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.