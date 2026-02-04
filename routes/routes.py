from fastapi import FastAPI, HTTPException, Request
from dto import ChatRequest
from google import genai
from google.genai import types
from tools import get_nearby_amenities_from_google_maps
from prompts import get_tourist_guide_prompt
from models import settings

app = FastAPI(title="Gemini Location Agent API")
client = genai.Client(api_key=settings.gemini_api_key)
history = dict()

@app.post("/api/chat")
async def chat_with_agent(request: Request):
    headers = request.headers
    if headers.get('Authorization') != 'Bearer app_chat_secret_!#@%':
        raise HTTPException(
            status_code=401,
            detail="Invalid source, this api just works with Tourist Guide Chat",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    body: ChatRequest = await request.json()
    try:
        if len(body.get('chatHistory') or []) > 0:
            gemini_history = [
            types.Content(role=msg.get('role'), parts=[types.Part(text=msg.get('content'))])
            for msg in body.get('chatHistory')
            ]
            chat = client.chats.create(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    tools=[get_nearby_amenities_from_google_maps],
                    system_instruction=get_tourist_guide_prompt(body.get('lat'), body.get('long'))
                ),
                history=gemini_history 
            )
        else: 
            chat = client.chats.create(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    tools=[get_nearby_amenities_from_google_maps],
                    system_instruction=get_tourist_guide_prompt(body.get('lat'), body.get('long'))
                )
            )
        
        response = chat.send_message(body.get('message').get('content'))
        
        return {"agent_response": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

