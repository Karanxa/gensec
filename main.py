import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import json
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URI = os.getenv("mongodb://localhost:27017/")
MODEL_ENDPOINT = os.getenv("chatgpt.com")
API_KEY = os.getenv("API_KEY")
DATABASE_NAME = "prompt_fuzzing_db"
COLLECTION_NAME = "fuzzing_results"

# Initialize MongoDB client
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

async def fetch_model_response(session, prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "prompt": prompt,
        "max_tokens": 150
    }
    async with session.post(MODEL_ENDPOINT, headers=headers, json=payload) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error from API: Status {response.status}")
            return None

async def process_prompt(session, prompt):
    try:
        response = await fetch_model_response(session, prompt)
        if response:
            result = {
                "prompt": prompt,
                "response": response.get("choices", [{}])[0].get("text"),
                "timestamp": datetime.utcnow()
            }
            await collection.insert_one(result)
            print(f"Processed prompt: {prompt[:30]}...")
        else:
            print(f"Failed to process prompt: {prompt[:30]}...")
    except Exception as e:
        print(f"Error processing prompt: {prompt[:30]}... Error: {str(e)}")

async def main():
    # Load prompts from a JSON file
    try:
        with open("prompts.json", "r") as f:
            prompts = json.load(f)
    except FileNotFoundError:
        print("prompts.json not found. Please create this file with your prompts.")
        return
    except json.JSONDecodeError:
        print("Error decoding prompts.json. Please ensure it's valid JSON.")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [process_prompt(session, prompt) for prompt in prompts]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())