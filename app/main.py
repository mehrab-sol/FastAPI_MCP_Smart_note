from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import engine, get_db, Base
from app.models import Note
from app.schemas import NoteCreate, NoteResponse, NoteSearchResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel
import os

# startup - connects with postgres and create the tables if not exist
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# fastapi creation and naming and connects to the startup
app = FastAPI(title="Smart Notepad API", lifespan=lifespan)


# CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# agent endpoint - defines the shape of data coming into the agent [we are sending message only]
class AgentRequest(BaseModel):
    message: str

# post endpoint - for the html message sending
@app.post("/agent")
async def agent_endpoint(req: AgentRequest):
    
    server_params = StdioServerParameters(
        command="python3", 
        args=["mcp_server.py"]
        )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            
            tools = await load_mcp_tools(session)

            llm = ChatOpenAI(
                model="minimax/minimax-m2.5:free", 
                base_url="https://openrouter.ai/api/v1", 
                api_key=os.getenv("OPENROUTER_API_KEY").strip(), 
                temperature=0.7)
            agent = create_react_agent(llm, tools)

            response = await agent.ainvoke({"messages": [{"role": "user", "content": req.message}]})
            return {"reply": response["messages"][-1].content}


# Check if title already exist if yes return a error else push the data and refreshes it to return id and timestamp
@app.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Note).where(Note.title == note.title))
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Note with this title already exists!")

    new_note = Note(title=note.title, content=note.content)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

# return all notes as a list
@app.get("/notes", response_model=list[NoteResponse])
async def get_notes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note))
    notes = result.scalars().all()
    return notes

# searching query endpoint
@app.get("/notes/search", response_model=NoteSearchResponse)
async def search_notes(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Note).where(
            or_(
                Note.title.ilike(f"%{q}%"),
                Note.content.ilike(f"%{q}%")
            )
        )
    )
    notes = result.scalars().all()
    return {"notes": notes, "total": len(notes)}

# delete end point
@app.delete("/notes/{title}")
async def delete_note(title: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Note).where(Note.title == title))
    note = result.scalar_one_or_none()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found!")

    await db.delete(note)
    await db.commit()
    return {"message": f"Note '{title}' deleted successfully!"}






