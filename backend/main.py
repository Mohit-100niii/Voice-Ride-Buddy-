from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
import json
import re
from router import recentride
from services.distance import get_distance_from_osm
from db.mongo import connect_db
from services.fare import get_fare;
from router import auth ; 
from router import payment;
from router import myrides

db_instance = connect_db()

load_dotenv()
app = FastAPI()

# CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow from all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"



app.include_router(auth.router,prefix="/auth")

app.include_router(payment.router,prefix="/api")
app.include_router(recentride.router,prefix="/api/get-last-ride")
app.include_router(myrides.router,prefix="/api")
@app.get("/test")
def read_root():
    return {"message": "🚀 FastAPI backend is working!"}

@app.post("/bookvoiceride")
async def parse_text(request: Request):
    body = await request.json()
    user_text = body.get("text")
    print("📥 Received voice input:", user_text)

    prompt = f"""
                You are a ride booking assistant. Extract structured ride info from user input.

                User: "{user_text}"

                Respond only in this JSON format:
                {{
                "pickup": "pickup location",
                "drop": "drop location",
                "time": "time mentioned",
                "date": "today/tomorrow/optional"
                "distance": "just give me Number Only  Distance btw this 2 points in km only"
                "expected fare":"just give me number range"
                }}
                """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-frontend-domain.com",  # put dummy if local
        "X-Title": "RideBuddyAI"
    }

    data = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 400,
    "temperature": 0.3
}


  
    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=data)
        result = response.json()
        
        print(result)

        try:
                gpt_reply = result["choices"][0]["message"]["content"]
                print("🧠 Raw GPT reply:", gpt_reply)

                # Extract JSON part only
                match = re.search(r'\{.*\}', gpt_reply, re.DOTALL)
                if not match:
                    raise ValueError("No valid JSON found in GPT reply.")

                cleaned_json = re.sub(r'//.*', '', match.group(0)) 
                parsed_data = json.loads(cleaned_json)
                distance_result = await get_distance_from_osm(parsed_data.get("pickup"), parsed_data.get("drop"))
                

               # Add it to your return only if it worked
                if "error" in distance_result:
                    parsed_distance = "Distance not available"
                else:
                    parsed_distance = f"{distance_result['distance_km']}"

                fare_calculate=await get_fare(parsed_distance);
                return {
                    "pickup": parsed_data.get("pickup"),
                    "drop": parsed_data.get("drop"),
                    "time": parsed_data.get("time"),
                    "date": parsed_data.get("date"),
                    "distance":parsed_distance,
                    "expected_fare": fare_calculate  # note: key has space
                }
        except:
                return {"error": "Server Error, Please Try Again", "raw": result}


