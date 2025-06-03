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
import datetime
from pathlib import Path
from fastapi import WebSocketDisconnect
import logging

# Import your existing chatbot components
from src.chatbot import MentalHealthChatbot
from src.memory_manager import MentalHealthMemoryManager

# Configure logging
# Basic configuration if not already elaborately configured
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("main.py: Script execution started.")

# Create the FastAPI app
app = FastAPI(
    title="Mindful Companion API",
    description="A professional mental health support chatbot.",
    version="1.0.0"
)
logger.info("main.py: FastAPI app created.")

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

logger.info("main.py: Attempting to initialize MentalHealthChatbot...")
# Initialize chatbot
chatbot = MentalHealthChatbot()
logger.info("main.py: MentalHealthChatbot initialized successfully.")

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
    logger.info(f"main.py: websocket_endpoint called for client_id: {client_id}")
    await websocket.accept()
    active_connections[client_id] = websocket
    logger.info(f"WebSocket connected for client: {client_id}")
    
    # Send initial greeting or load existing conversation
    if not chatbot.memory.get_formatted_history(client_id):
        logger.info(f"main.py: [{client_id}] New conversation detected. Starting conversation setup.")
        greeting = chatbot.start_conversation(client_id) 
        logger.info(f"main.py: [{client_id}] Greeting generated: '{greeting[:50]}...'. Attempting to send.") # Log part of greeting
        try:
            await websocket.send_json({
                "type": "message",
                "content": greeting,
                "timestamp": time.time(),
                "sender": "bot"
            })
            logger.info(f"main.py: [{client_id}] Initial greeting sent successfully.")
        except Exception as e:
            logger.error(f"main.py: [{client_id}] Exception during initial send_json: {e}", exc_info=True)
            # Optionally re-raise or handle if the connection should close
    else:
        logger.info(f"main.py: [{client_id}] Existing conversation detected. Sending connection confirmation.")
        try:
            await websocket.send_json({
                "type": "system",
                "content": "Connected to existing conversation",
                "timestamp": time.time()
            })
            logger.info(f"main.py: [{client_id}] Existing conversation confirmation sent.")
        except Exception as e:
            logger.error(f"main.py: [{client_id}] Exception during existing conversation send_json: {e}", exc_info=True)
    
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
                        logger.error(f"Error processing message: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "content": "Sorry, I encountered an issue while processing your message. Please try again.",
                            "timestamp": time.time()
                        })
            except json.JSONDecodeError:
                logger.error(f"Received invalid JSON: {data}")
                continue
    except WebSocketDisconnect:
        # Handle normal disconnection
        logger.info(f"WebSocket disconnected for client: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Remove from active connections whether closed or not
        if client_id in active_connections:
            del active_connections[client_id]
        # DO NOT call await websocket.close() here as it might already be closed

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

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations."""
    try:
        conversations = chatbot.memory.get_all_conversations()
        return conversations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversations: {str(e)}")

@app.get("/api/conversations/{user_id}")
async def get_conversation(user_id: str):
    """Get a specific conversation."""
    try:
        messages = chatbot.memory.get_conversation_messages(user_id)
        user_details = chatbot.memory.get_user_details(user_id)
        
        # If both messages and user_details are empty, it implies the user_id is not found
        # or represents no actual conversation data.
        if not messages and not user_details:
            raise HTTPException(status_code=404, detail=f"Conversation not found for user_id: {user_id}")
            
        return {
            "messages": messages,
            "user_details": user_details
        }
    except HTTPException: # Re-raise HTTPException to ensure FastAPI handles it
        raise
    except Exception as e:
        # Log the full error with traceback for unexpected errors
        import traceback
        error_details = traceback.format_exc()
        # Using logger if available, otherwise print
        try:
            logger.error(f"Error retrieving conversation for {user_id}: {str(e)}\n{error_details}")
        except NameError: # logger might not be defined if this snippet is run standalone
            print(f"Error retrieving conversation for {user_id}: {str(e)}\n{error_details}")
        
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")

@app.post("/api/conversations/new")
async def create_new_conversation():
    """Create a new conversation."""
    try:
        # Generate a unique user ID with timestamp and UUID
        user_id = f"user_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Initialize an empty conversation in memory
        chatbot.memory.clear_history(user_id)
        
        # Start the conversation with initial greeting
        greeting = chatbot.start_conversation(user_id)
        
        # Store the initial greeting in memory
        chatbot.memory.add_bot_message(user_id, greeting)
        
        # Return success response with user ID and timestamp
        return {
            "user_id": user_id,
            "created_at": datetime.datetime.now().isoformat(),
            "initial_message": greeting,
            "success": True
        }
    except Exception as e:
        # Log the full error with traceback
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error creating new conversation: {str(e)}\n{error_details}")
        
        # Return error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create new conversation",
                "message": str(e)
            }
        )

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)