from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from identity import AgentIdentity

# Identity & Configuration
provider_identity = AgentIdentity()
MIN_ACCEPTABLE_PRICE = 0.005
REGISTRY_URL = "http://127.0.0.1:8000"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def ask_ollama_decision(task_description: str, offered_price: float) -> dict:
    """
    Query local Ollama instance with a strict system prompt.
    """
    # Decision logic in plain Python first for safety
    if offered_price < MIN_ACCEPTABLE_PRICE:
        return {"decision": "REJECT", "raw": "Price below minimum threshold"}

    # Precise Prompt for Ollama
    prompt = (
        f"Task: {task_description}. "
        f"Price offered: ${offered_price}. "
        f"Minimum required: ${MIN_ACCEPTABLE_PRICE}. "
        "Is the offer price equal to or greater than minimum required? "
        "Answer with strictly ONE word: ACCEPT or REJECT."
    )
    
    try:
        res = httpx.post(OLLAMA_URL, json={
            "model": "qwen2.5-coder:1.5b",  # Replace with your local model tag if different
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.0}  # Deterministic output
        }, timeout=10.0)
        
        ai_response = res.json().get("response", "").strip().upper()
        print(f"[OLLAMA RAW RESPONSE]: '{ai_response}'")
        
        decision = "ACCEPT" if "ACCEPT" in ai_response else "REJECT"
        return {"decision": decision, "raw": ai_response}
    except Exception as e:
        print(f"[OLLAMA WARNING] Fallback to rule engine: {e}")
        return {"decision": "ACCEPT" if offered_price >= MIN_ACCEPTABLE_PRICE else "REJECT"}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Modern FastAPI startup handler
    endpoint = "http://127.0.0.1:8001"
    reg_payload = f"REGISTER:{provider_identity.did}:{endpoint}"
    signature = provider_identity.sign_message(reg_payload)
    
    payload = {
        "did": provider_identity.did,
        "capabilities": ["gpu_inference", "llm_eval"],
        "endpoint": endpoint,
        "pricing": {"min_price": MIN_ACCEPTABLE_PRICE},
        "signature": signature
    }
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{REGISTRY_URL}/register", json=payload)
            print(f"[PROVIDER STARTED] Registered to Registry -> DID: {provider_identity.did}")
        except Exception as e:
            print(f"[ERROR] Registry connection failed: {e}")
    yield

app = FastAPI(title="AI-Powered Provider Agent Node", lifespan=lifespan)

class ServiceOrder(BaseModel):
    buyer_did: str
    target_did: str
    service: str
    max_price: float
    timestamp: int
    payload_string: str
    signature: str

@app.post("/execute")
def process_order(order: ServiceOrder):
    # 1. Cryptographic Verification
    if not AgentIdentity.verify_signature(order.buyer_did, order.payload_string, order.signature):
        raise HTTPException(status_code=401, detail="INVALID_SIGNATURE")

    # 2. AI Reasoning via Ollama
    ai_result = ask_ollama_decision(order.service, order.max_price)
    
    if ai_result["decision"] == "REJECT":
        raise HTTPException(status_code=400, detail="REJECTED_BY_AI_AGENT")

    return {
        "status": "ACCEPTED",
        "message": f"Execution approved by Provider AI ({provider_identity.did[:15]}...)",
        "settled_price": order.max_price,
        "ai_reasoning": ai_result["decision"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)