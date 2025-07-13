import logging
import sys
import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.callbacks import BaseCallbackHandler
from typing import AsyncIterable, Optional, List, Any, Dict


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)
logger = logging.getLogger(__name__)

class ToolCallbackHandler(BaseCallbackHandler):
    """A custom callback handler to record which tools are used."""
    def __init__(self):
        super().__init__()
        self.used_tools = []

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Called when the agent is about to start using a tool."""
        tool_name = serialized.get("name")
        logger.info(f"Agent is using tool: {tool_name}")
        self.used_tools.append(tool_name)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ChatRequest(BaseModel):
    query: str
    history: list[str] = []  

async def run_agent_with_query(query: str, history: list[str] = []) -> str:
    client = MCPClient.from_config_file("backend/elasticsearch_mcp.json")
    llm = AzureChatOpenAI(
        openai_api_version="2025-01-01-preview",
        azure_deployment="gpt-4o",
        azure_endpoint="https://example.openai.azure.com/",
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

   
    system_prompt = (
        "You are a helpful and knowledgeable librarian, equipped with tools to assist users with their book inquiries. " +
        "You have access to the Elastic MCP server with the 'books' index" +
        "Your available tools are:\n" +
        "- **search**: Use this tool to find general information about books within the 'books' Elasticsearch index. When using this tool, you MUST provide both `index` (which should be 'books') and a valid Elasticsearch `queryBody` (e.g., using a `match` query, `bool` query, etc.). Remove any case formatting in the query body. Never return more than 5 results at any one time and always present the results in a human readable way. You can bold the title. \n" +
        "- **list_indices**, **get_mappings**, **get_shards**: (Not usually needed—only if the user explicitly requests low-level Elasticsearch details.)\n\n" +
        "**Important formatting rule:**"
        "1. Render each book as its own numbered card or entry."
        "2. **Any text that isn’t part of a specific book entry**—for example, a final wrap-up, recommendation, or “next steps” paragraph—**must begin with the header**:"
        "Additional Notes:"
        "and then that text.  Do not include that under any numbered item or card."
        "After using a tool, begin your answer with “Using the [tool_name] tool, …” etc."
        "After retrieving information using any tool, explain the results clearly and engagingly, like a human librarian would:\n" +
        "- Compare or contrast books clearly, if multiple are found.\n" +
        "- Highlight themes, readability, or significance of the books.\n" +
        "- Format your responses so they're easy to read and inviting.\n" +
        "- Avoid just listing raw fields; interpret the data for the user.\n" +
        "- It's okay to express a gentle opinion or help guide the user to their next read.\n" +
        "- Speak naturally, like you're helping a curious reader at the reference desk.\n\n" +
        "If multiple books are found by any tool, summarize each one clearly in plain English.\n\n" +
        "After using a tool, you MUST begin your final answer with **'Using the [tool_name] tool, '** where [tool_name] is exactly the tool you invoked (for example, 'Using the search tool, I found…'). " +
        "If you did not use a tool, just answer directly."
        )

    agent = MCPAgent(llm=llm, client=client, max_steps=30, system_prompt=system_prompt)

    full_prompt = "\n".join(history + [query])

    try:
        return await agent.run(full_prompt)
    finally:
        await client.close_all_sessions()

@app.post("/api/books-chat")
async def books_chat_endpoint(req: ChatRequest, http_request: Request):
    try:
        response = await run_agent_with_query(req.query, req.history)
        return {"response": response}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/")
async def root():
    logger.info("Root endpoint '/' accessed.")
    return {"message": "ES Book server is running."}
