"""
Pioneer + OpenAI Integration Example
A simple chat application demonstrating personalization with Fastino's Pioneer API
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configuration
PIONEER_API_KEY = os.getenv("PIONEER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PIONEER_BASE_URL = "https://api.fastino.ai"

if not PIONEER_API_KEY:
    raise ValueError("PIONEER_API_KEY environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI(title="Pioneer + OpenAI Chat Example")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []
    user_id: Optional[str] = None
    user_email: Optional[str] = None  # For debugging/logging only

class ChatResponse(BaseModel):
    response: str
    relevant_context: Optional[List[Dict]] = None
    user_profile: Optional[str] = None

class RegisterUserRequest(BaseModel):
    email: str
    name: Optional[str] = None
    timezone: Optional[str] = None

# Helper Functions
def get_pioneer_headers():
    """Get headers for Pioneer API requests"""
    return {
        "x-api-key": PIONEER_API_KEY,
        "Content-Type": "application/json"
    }

async def register_pioneer_user(email: str, name: Optional[str] = None, timezone: Optional[str] = None):
    """Register a user with Pioneer API"""
    async with httpx.AsyncClient() as client:
        payload = {
            "email": email,
            "purpose": "A personalized AI chat assistant that learns from conversations and adapts to user preferences",
            "traits": {}
        }
        
        if name:
            payload["traits"]["name"] = name
        if timezone:
            payload["traits"]["timezone"] = timezone
            
        response = await client.post(
            f"{PIONEER_BASE_URL}/register",
            headers=get_pioneer_headers(),
            json=payload,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to register user with Pioneer: {response.text}"
            )
        
        return response.json()

async def get_user_summary(user_id: str, max_chars: int = 1000) -> Optional[str]:
    """Get user profile summary from Pioneer"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{PIONEER_BASE_URL}/summary",
                headers=get_pioneer_headers(),
                params={"user_id": user_id, "max_chars": max_chars},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("summary")
            else:
                print(f"[ERROR] Failed to get user summary. Status: {response.status_code}, Response: {response.text}")
            return None
        except Exception as e:
            print(f"[ERROR] Exception fetching user summary: {e}")
            return None

async def get_relevant_chunks(user_id: str, conversation_history: List[Dict], k: int = 5):
    """Get relevant context chunks from Pioneer"""
    async with httpx.AsyncClient() as client:
        try:
            # Format history for Pioneer API
            history = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in conversation_history
            ]
            
            response = await client.post(
                f"{PIONEER_BASE_URL}/chunks",
                headers=get_pioneer_headers(),
                json={
                    "user_id": user_id,
                    "history": history,
                    "k": k,
                    "similarity_threshold": 0.25
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("chunks", [])
            else:
                print(f"[ERROR] Failed to get chunks. Status: {response.status_code}, Response: {response.text}")
            return []
        except Exception as e:
            print(f"[ERROR] Exception fetching chunks: {e}")
            return []

async def ingest_conversation(user_id: str, messages: List[Dict]):
    """Ingest conversation into Pioneer for learning"""
    async with httpx.AsyncClient() as client:
        try:
            # Format messages for Pioneer
            formatted_messages = []
            for msg in messages:
                formatted_msg = {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp", datetime.utcnow().isoformat() + "Z")
                }
                formatted_messages.append(formatted_msg)
            
            response = await client.post(
                f"{PIONEER_BASE_URL}/ingest",
                headers=get_pioneer_headers(),
                json={
                    "user_id": user_id,
                    "source": "chat_app",
                    "message_history": formatted_messages,
                    "options": {"dedupe": True}
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                print(f"[ERROR] Failed to ingest conversation. Status: {response.status_code}, Response: {response.text}")
            else:
                print(f"[SUCCESS] Conversation ingested successfully")
        except Exception as e:
            print(f"[ERROR] Exception ingesting conversation: {e}")

async def query_user_knowledge(user_id: str, question: str, use_cache: bool = True) -> Optional[str]:
    """
    Query the Pioneer API to ask questions about the user's knowledge base.
    This allows the agent to ask specific questions and get detailed answers
    about the user's context, relationships, preferences, etc.
    
    Args:
        user_id: The user's ID
        question: The question to ask about the user
        use_cache: Whether to use cached results (default: True)
        
    Returns:
        The answer to the question, or None if the query failed
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PIONEER_BASE_URL}/query",
                headers=get_pioneer_headers(),
                json={
                    "user_id": user_id,
                    "question": question,
                    "use_cache": use_cache
                },
                timeout=180.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("answer")
            else:
                print(f"[ERROR] Failed to query user knowledge. Status: {response.status_code}, Response: {response.text}")
                return None
        except Exception as e:
            print(f"[ERROR] Exception querying user knowledge: {e}")
            return None

# Tool definitions for OpenAI function calling
QUERY_TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "query_user_knowledge",
        "description": "Query the user's knowledge base to ask specific questions about their preferences, relationships, professional network, communication patterns, and other contextual information. Use this only when you need detailed information about the user that may not be in the general profile summary or messages",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "A specific question to ask about the user. Examples: 'Who are the most important people in the user's professional network?', 'What are the user's communication preferences?', 'What topics does the user discuss most frequently?'"
                }
            },
            "required": ["question"]
        }
    }
}

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Pioneer + OpenAI Chat API",
        "endpoints": {
            "/chat": "POST - Send a message and get personalized response",
            "/register": "POST - Register a new user",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/register", response_model=Dict)
async def register_user(request: RegisterUserRequest):
    """Register a new user with Pioneer"""
    try:
        result = await register_pioneer_user(
            email=request.email,
            name=request.name,
            timezone=request.timezone
        )
        return {
            "success": True,
            "user_id": result.get("user_id"),
            "message": f"User {request.email} registered successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message with personalization from Pioneer
    
    This endpoint:
    1. Retrieves user profile summary from Pioneer
    2. Gets relevant context chunks based on conversation history
    3. Sends enhanced prompt to OpenAI GPT-4o
    4. Ingests the conversation back to Pioneer for learning
    """
    try:
        # User ID is required - user must register first on frontend
        if not request.user_id:
            raise HTTPException(
                status_code=400, 
                detail="user_id is required. Please register on the frontend first."
            )
        
        user_id = request.user_id
        user_email = request.user_email  # For logging only
        
        print(f"[DEBUG] Processing chat for user_id: {user_id}, email: {user_email}")
        
        # Note: No need to re-register here - user_id was obtained during initial registration
        
        # Get user profile summary
        print(f"[DEBUG] Fetching user summary for user_id: {user_id}")
        user_summary = await get_user_summary(user_id)
        print(f"[DEBUG] User summary: {user_summary[:100] if user_summary else 'None'}")
        
        # Build conversation history
        conversation = [msg.model_dump() for msg in request.conversation_history]
        conversation.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # Get relevant context chunks
        print(f"[DEBUG] Fetching relevant chunks for user_id: {user_id}")
        chunks = await get_relevant_chunks(user_id, conversation)
        print(f"[DEBUG] Retrieved {len(chunks)} chunks")
        
        # Build system prompt with personalization
        system_prompt = "You are a helpful AI assistant."
        if user_summary:
            system_prompt += f"\n\nUser Profile:\n{user_summary}\n\nKeep the user's preferences and context in mind when responding."
            print(f"[DEBUG] Added user profile to system prompt")
        
        # Build user message with context
        user_message = request.message
        if chunks:
            context_text = "\n".join([f"- {chunk['text']}" for chunk in chunks])
            user_message += f"\n\n[Relevant context from past conversations:\n{context_text}]"
            print(f"[DEBUG] Added {len(chunks)} context chunks to user message")
        
        # Call OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Add current message with context
        messages.append({"role": "user", "content": user_message})
        
        completion = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            tools=[QUERY_TOOL_DEFINITION],  # Enable the query tool if needed. Since this demo is limited in data scope, we will not use it.
        )
        
        assistant_response = completion.choices[0].message.content
        
        # Add assistant response to conversation for ingestion
        conversation.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        
        # Ingest conversation back to Pioneer (async, don't wait)
        # In production, you might want to do this in a background task
        print(f"[DEBUG] Ingesting conversation for user_id: {user_id}")
        await ingest_conversation(user_id, conversation)
        print(f"[DEBUG] Conversation ingestion completed")
        
        return ChatResponse(
            response=assistant_response,
            relevant_context=chunks if chunks else None,
            user_profile=user_summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

