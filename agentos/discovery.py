import time
from typing import Dict, List, Optional
from agentos.identity import AgentIdentity

class DiscoveryRegistry:
    """
    Centralized lightweight directory node for Agent OS network.
    Maintains registered agents, their capabilities, endpoints, and DIDs.
    """
    def __init__(self):
        # In-memory database of registered agents
        self._registry: Dict[str, dict] = {}

    def register_agent(
        self, 
        did: str, 
        capabilities: List[str], 
        endpoint: str, 
        pricing: dict, 
        signature: str
    ) -> bool:
        """
        Registers a new agent in the network after verifying its identity signature.
        """
        registration_payload = f"REGISTER:{did}:{endpoint}"
        
        # Verify that the registration request was signed by the key owner
        if not AgentIdentity.verify_signature(did, registration_payload, signature):
            print(f"[REGISTRY ERROR] Signature verification failed for DID: {did}")
            return False

        # Store agent metadata in the registry
        self._registry[did] = {
            "did": did,
            "capabilities": capabilities,
            "endpoint": endpoint,
            "pricing": pricing,
            "status": "ACTIVE",
            "last_seen": time.time()
        }
        print(f"[REGISTRY SUCCESS] Agent registered successfully -> DID: {did}")
        return True

    def discover_agents(self, required_capability: str) -> List[dict]:
        """
        Searches and returns active agents offering a specific capability.
        """
        matches = []
        for agent in self._registry.values():
            if required_capability in agent["capabilities"] and agent["status"] == "ACTIVE":
                matches.append(agent)
        return matches

    def get_agent_by_did(self, did: str) -> Optional[dict]:
        """Retrieves specific agent metadata by its unique DID."""
        return self._registry.get(did)


# --- Local testing and verification ---
if __name__ == "__main__":
    print("--- 1. Initializing Agent OS Discovery Registry ---")
    registry = DiscoveryRegistry()

    print("\n--- 2. Creating Provider Agent (GPU Service) ---")
    gpu_agent_identity = AgentIdentity()
    gpu_did = gpu_agent_identity.did
    gpu_endpoint = "grpc://127.0.0.1:50051"
    
    # Sign registration payload
    reg_payload = f"REGISTER:{gpu_did}:{gpu_endpoint}"
    reg_signature = gpu_agent_identity.sign_message(reg_payload)

    # Register Provider Agent in the network
    registry.register_agent(
        did=gpu_did,
        capabilities=["gpu_inference", "llm_qwen2.5"],
        endpoint=gpu_endpoint,
        pricing={"rate_per_token": 0.000001, "currency": "USD"},
        signature=reg_signature
    )

    print("\n--- 3. Consumer Agent Querying Discovery Registry ---")
    search_capability = "gpu_inference"
    discovered_agents = registry.discover_agents(required_capability=search_capability)
    
    print(f"Querying for capability: '{search_capability}'")
    print(f"Discovered Agents Count: {len(discovered_agents)}")
    if discovered_agents:
        target = discovered_agents[0]
        print(f"Found Provider Agent DID: {target['did']}")
        print(f"Endpoint: {target['endpoint']}")
        print(f"Pricing Model: {target['pricing']}")
    
    print("\n--- 4. Testing Unauthorized Registration Attempt ---")
    fraudulent_identity = AgentIdentity()
    fake_signature = "INVALID_SIGNATURE_STRING"
    
    unauthorized_success = registry.register_agent(
        did=fraudulent_identity.did,
        capabilities=["data_analysis"],
        endpoint="grpc://127.0.0.1:50052",
        pricing={"rate_per_task": 1.0},
        signature=fake_signature
    )
    print(f"Is unauthorized registration accepted? -> {unauthorized_success}")