# Elastic Book Chat

Elastic Book Chat is a conversational book recommendation demo using:

- Azure OpenAI (GPT-4o)
- Elastic with MCP (https://github.com/elastic/mcp-server-elasticsearch?tab=readme-ov-file)
- FastAPI backend
- Vite + React frontend

It allows users to query a book database in natural language and receive helpful, librarian-style responses powered by real search results.

---

## Features

- Natural language search over books via Elastic MCP
- GPT-4o used for response generation and formatting
- Clear, human-readable summaries of books
- Remembers recent chat history
- Clean, responsive user interface

---

## Tech Stack

| Component    | Technology                  |
|--------------|-----------------------------|
| Frontend     | React                |
| Backend      | FastAPI (Python 3.11)       |
| Search       | Elastic MCP + Elastics |
| LLM          | Azure OpenAI (GPT-4o)       |
| Agent Engine | LangChain MCPAgent          |

---

## Getting Started

Pre-reqs: 
- Elasticsearch cluster
- Python 3.11
- Kaggle API key (optional - see below)
- Azure openAI key

### Set Up and Data Ingest
1. Clone the repository

```
git https://github.com/camillegeorgiou/mcp-demo
cd mcp-demo
```

2. Set up the Python backend

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Modify .env file

```
AZURE_OPENAI_API_KEY=your_azure_openai_key
ES_URL=your_elastic_url
ES_API_KEY=elastic_api
```

4. Navigate to kaggle, spin up an account and download an api key
- alternatiely, you can download the books csv and modify the script to push the dataset to Elastic.

5. Run the books.py and confirm data has made it into your cluster.

### Backend 

6. Add MCP config to backend/elasticsearch_mcp.json
- Modify elasticsearch_mcp to include your ES credentials. The API key should have relevant permissions. See: https://github.com/elastic/mcp-server-elasticsearch?tab=readme-ov-file

7. Start the backend
```
uvicorn backend.server:app --reload
```

- You should see the following output (or similar):

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [15448] using StatReload
INFO:     Started server process [15450]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

# Frontend Setup
In a separate terminal:

```
cd bookchat-frontend 
npm install
npm run dev
```

- The app will be available at http://localhost:5173.

## Sample Queries
What are the best books on computing?
Which books have the highest rating?
Any good biographies for young readers?

