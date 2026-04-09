from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Smart Notepad")

BASE_URL = "http://127.0.0.1:8000"

@mcp.tool()
async def add_note(title: str, content: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/notes",
            json={"title": title, "content": content}
        )
        if response.status_code == 200:
            return f"Note '{title}' saved successfully!"
        return f"Error: {response.json()['detail']}"
    

@mcp.tool()
async def get_notes() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/notes")
        notes = response.json()

        if not notes:
            return "No notes found!"

        output = ""
        for i, note in enumerate(notes, start=1):
            output += f"{i}. {note['title']}: {note['content']}\n"

        return output
    
@mcp.tool()
async def search_note(query: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/notes/search",
            params={"q": query}
        )
        data = response.json()

        if data["total"] == 0:
            return "No matching notes found!"

        output = ""
        for i, note in enumerate(data["notes"], start=1):
            output += f"{i}. {note['title']}: {note['content']}\n"

        return output
    

@mcp.tool()
async def delete_note(title: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/notes/{title}")

        if response.status_code == 200:
            return f"Note '{title}' deleted successfully!"
        return f"Error: {response.json()['detail']}"
    

    
if __name__ == "__main__":
    mcp.run(transport="stdio")