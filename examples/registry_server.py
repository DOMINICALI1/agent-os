import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from identity import AgentIdentity

app = FastAPI(title="Agent OS Discovery Registry")

# In-memory storage for active network nodes
registry_db: Dict[str, dict] = {}

class RegisterRequest(BaseModel):
    did: str
    capabilities: List[str]
    endpoint: str
    pricing: dict
    signature: str

@app.post("/register")
def register_agent(req: RegisterRequest):
    registration_payload = f"REGISTER:{req.did}:{req.endpoint}"
    
    # Verify cryptographic signature
    if not AgentIdentity.verify_signature(req.did, registration_payload, req.signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    registry_db[req.did] = {
        "did": req.did,
        "capabilities": req.capabilities,
        "endpoint": req.endpoint,
        "pricing": req.pricing,
        "status": "ACTIVE",
        "last_seen": time.time()
    }
    print(f"[REGISTRY] Agent registered: {req.did} at {req.endpoint}")
    return {"status": "SUCCESS", "did": req.did}

@app.get("/discover")
def discover_agents(capability: str):
    matches = [
        agent for agent in registry_db.values()
        if capability in agent["capabilities"] and agent["status"] == "ACTIVE"
    ]
    return {"count": len(matches), "agents": matches}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)