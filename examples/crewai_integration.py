import os
import asyncio
from crewai import Agent, Task, Crew, Process
from agentos_net.sdk import AgentOSClient, ProtocolConfig
from agentos_net.crypto import KeysManager

# Initialize Cryptographic Identity (Ed25519)
keys = KeysManager.generate_keypair()
agent_did = f"did:agentos:{keys.public_key_hex[:16]}"

# Initialize AgentOS Transport Client (gRPC Protocol)
config = ProtocolConfig(
    host="127.0.0.1",
    port=50051,
    enable_tls=False
)
client = AgentOSClient(config=config, identity_did=agent_did, private_key=keys.private_key_pem)

# Define CrewAI Negotiation Agent
negotiator = Agent(
    role="Protocol Negotiation Specialist",
    goal="Negotiate task execution rates and payload specifications via agentos-net",
    backstory="You are an autonomous interface node that verifies DIDs and negotiates tasks over gRPC transport.",
    verbose=True,
    allow_delegation=False
)

# Define CrewAI Task
negotiation_task = Task(
    description=f"Initiate DID handshake for target DID 'did:agentos:provider_node_01' and negotiate a 1000 request payload batch.",
    expected_output="Cryptographically signed agreement payload ready for execution.",
    agent=negotiator
)

def run_integration():
    # Connect AgentOS Transport Layer
    connected = client.connect()
    if not connected:
        print("[AgentOS] Failed to establish gRPC transport channel.")
        return

    print(f"[AgentOS] Identity verified: {agent_did}")
    
    # Execute CrewAI Workflow
    crew = Crew(
        agents=[negotiator],
        tasks=[negotiation_task],
        process=Process.sequential
    )
    
    result = crew.kickoff()
    print("[CrewAI Output]:", result)
    
    # Broadcast Negotiated Payload over AgentOS Protocol
    response = client.send_proposal(
        target_did="did:agentos:provider_node_01",
        payload={"task_data": str(result), "rate_limit": 100}
    )
    print(f"[AgentOS Handshake Status]: {response.status}")

if __name__ == "__main__":
    run_integration()