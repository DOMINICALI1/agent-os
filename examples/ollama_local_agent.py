import json
import time
from agentos_net.sdk import AgentOSClient, ProtocolConfig
from agentos_net.crypto import KeysManager

# 1. Initialize Local Cryptographic Identity
agent_keys = KeysManager.generate_keypair()
ollama_agent_did = f"did:agentos:{agent_keys.public_key_hex[:16]}"

class OllamaAgentNode:
    """
    Wraps a local Ollama model execution into an AgentOS network node.
    Enables low-latency gRPC task handling for local LLMs.
    """
    def __init__(self, model_name="qwen2.5-coder:1.5b", port=50052):
        self.model_name = model_name
        self.port = port
        self.did = ollama_agent_did

    def process_incoming_grpc_request(self, payload: dict) -> dict:
        """
        Simulates receiving a gRPC request from another local agent (e.g., CrewAI)
        and processing it via local LLM inference.
        """
        prompt = payload.get("prompt", "")
        sender_did = payload.get("sender_did", "unknown")
        
        print(f"[Ollama Node | {self.did}] Received task from: {sender_did}")
        print(f"[Ollama Node] Executing local inference using '{self.model_name}'...")

        # Simulated local inference response
        execution_time_ms = 42
        result_text = f"Processed locally via {self.model_name}: Result for '{prompt}'"

        return {
            "status": "success",
            "result": result_text,
            "metrics": {
                "latency_ms": execution_time_ms,
                "engine": "ollama_local"
            },
            "signed_by": self.did
        }

def run_ollama_integration_demo():
    node = OllamaAgentNode()
    
    # Payload arriving from a remote/local partner agent (e.g. CrewAI Agent)
    incoming_payload = {
        "sender_did": "did:agentos:a1b2c3d4e5f67890",
        "task_type": "code_optimization",
        "prompt": "Optimize VRAM usage for local LLM inference"
    }

    start_time = time.time()
    response = node.process_incoming_grpc_request(incoming_payload)
    elapsed = (time.time() - start_time) * 1000

    print("\n--- AgentOS Local Response Handshake ---")
    print(json.dumps(response, indent=2))
    print(f"Total Handshake Time: {elapsed:.2f} ms")

if __name__ == "__main__":
    run_ollama_integration_demo()