from fastapi import FastAPI, WebSocket, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Optional, List
import uuid
import time
import json
import os
import asyncio
from pathlib import Path

# Import your existing chatbot components
from src.chatbot import MentalHealthChatbot
from src.memory_manager import MentalHealthMemoryManager

# Create the FastAPI app
app = FastAPI(
    title="Mindful Companion API",
    description="A professional mental health support chatbot.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize chatbot
chatbot = MentalHealthChatbot()

# Active connections
active_connections: Dict[str, WebSocket] = {}

# Serve the main HTML page
@app.get("/")
async def get_index():
    return FileResponse('static/index.html')

# Serve favicon
@app.get("/favicon.ico")
async def get_favicon():
    favicon_path = Path("static/favicon.png")
    if favicon_path.exists():
        return FileResponse(favicon_path)
    else:
        # If specific favicon not found, try to find any favicon in static directory
        for path in Path("static").glob("favicon.*"):
            return FileResponse(path)
        # Default response if no favicon found
        raise HTTPException(status_code=404, detail="Favicon not found")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    # Send initial greeting
    greeting = chatbot.start_conversation(client_id)
    await websocket.send_json({
        "type": "message",
        "content": greeting,
        "timestamp": time.time(),
        "sender": "bot"
    })
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get('type') == 'message':
                    user_text = message.get('text', '').strip()
                    
                    # Skip empty messages
                    if not user_text:
                        continue
                    
                    # Handle special commands
                    if user_text.lower() == 'clear':
                        chatbot.memory.clear_history(client_id)
                        await websocket.send_json({
                            "type": "system",
                            "content": "Conversation history has been cleared.",
                            "timestamp": time.time()
                        })
                        continue
                    
                    # Process message
                    try:
                        # Add a small delay to simulate thinking (optional)
                        await asyncio.sleep(0.5)
                        
                        # Get response from chatbot
                        response = chatbot.process_message(
                            message=user_text,
                            user_id=client_id
                        )
                        
                        # Send response back to client
                        await websocket.send_json({
                            "type": "message",
                            "content": response,
                            "timestamp": time.time(),
                            "sender": "bot"
                        })
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "content": "Sorry, I encountered an issue while processing your message. Please try again.",
                            "timestamp": time.time()
                        })
            except json.JSONDecodeError:
                print(f"Received invalid JSON: {data}")
                continue
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if client_id in active_connections:
            del active_connections[client_id]
        await websocket.close()

@app.post("/clear_history/{client_id}")
async def clear_history(client_id: str):
    """Clear the conversation history for a specific client."""
    try:
        chatbot.memory.clear_history(client_id)
        return {"status": "success", "message": "Conversation history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@app.get("/debug/{client_id}")
async def get_debug_info(client_id: str):
    """Get debug information about a client's conversation history."""
    try:
        details = chatbot.get_user_details(client_id)
        history = chatbot.get_conversation_history(client_id)
        
        return {
            "client_id": client_id,
            "user_details": details,
            "history_length": len(history.split("\n\n")) if history else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving debug info: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "active_connections": len(active_connections)
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)