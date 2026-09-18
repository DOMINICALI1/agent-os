import time
from agentos.identity import AgentIdentity
from agentos.discovery import DiscoveryRegistry

class AgentNode:
    """
    Represents an autonomous agent node capable of buying or selling services,
    verifying cryptographic signatures, and handling peer-to-peer handshakes.
    """
    def __init__(self, name: str, budget: float = 0.0):
        self.name = name
        self.identity = AgentIdentity()
        self.did = self.identity.did
        self.budget = budget

    def create_service_request(self, target_did: str, service: str, max_price: float) -> dict:
        """
        Creates and signs a formal purchase agreement/payload for a target agent service.
        """
        timestamp = int(time.time())
        # Canonical string structure for signing
        payload_string = f"BUY_SERVICE:{self.did}:{target_did}:{service}:{max_price}:{timestamp}"
        signature = self.identity.sign_message(payload_string)
        
        return {
            "buyer_did": self.did,
            "target_did": target_did,
            "service": service,
            "max_price": max_price,
            "timestamp": timestamp,
            "payload_string": payload_string,
            "signature": signature
        }

    def process_incoming_request(self, request: dict, min_acceptable_price: float) -> dict:
        """
        Provider Agent evaluates and executes incoming buy requests.
        Verifies signature, budget limits, and authentication.
        """
        buyer_did = request["buyer_did"]
        payload_string = request["payload_string"]
        signature = request["signature"]
        offered_price = request["max_price"]

        # Step 1: Verify cryptographic signature
        if not AgentIdentity.verify_signature(buyer_did, payload_string, signature):
            return {"status": "REJECTED", "reason": "INVALID_CRYPTOGRAPHIC_SIGNATURE"}

        # Step 2: Negotiate price constraints
        if offered_price < min_acceptable_price:
            return {"status": "REJECTED", "reason": "PRICE_BELOW_MINIMUM_THRESHOLD"}

        # Step 3: Accept agreement & confirm execution
        return {
            "status": "ACCEPTED",
            "transaction_id": f"tx_{int(time.time())}",
            "executed_by": self.did,
            "settled_price": offered_price
        }


# --- End-to-End Handshake Simulation ---
if __name__ == "__main__":
    print("==================================================")
    print("   AGENT OS: END-TO-END HANDSHAKE SIMULATION      ")
    print("==================================================\n")

    # 1. Initialize Global Discovery Registry
    registry = DiscoveryRegistry()

    # 2. Setup Provider Agent (Seller)
    provider = AgentNode(name="CloudGPU_Provider", budget=0.0)
    provider_endpoint = "grpc://127.0.0.1:50051"
    provider_min_price = 0.005

    # Register Provider to Registry
    reg_payload = f"REGISTER:{provider.did}:{provider_endpoint}"
    reg_signature = provider.identity.sign_message(reg_payload)
    registry.register_agent(
        did=provider.did,
        capabilities=["gpu_inference"],
        endpoint=provider_endpoint,
        pricing={"min_price": provider_min_price},
        signature=reg_signature
    )
    print(f"\n[PROVIDER] Online: {provider.name} | DID: {provider.did}")

    # 3. Setup Consumer Agent (Buyer)
    consumer = AgentNode(name="User_Assistant_Agent", budget=5.00)
    print(f"[CONSUMER] Online: {consumer.name} | DID: {consumer.did} | Budget: ${consumer.budget}\n")

    # 4. Consumer discovers Provider via Registry
    print("--- Step 1: Discovering Services ---")
    discovered = registry.discover_agents("gpu_inference")
    target_agent_meta = discovered[0]
    target_did = target_agent_meta["did"]
    print(f"Consumer found active GPU provider -> DID: {target_did}\n")

    # 5. Consumer creates and signs purchase agreement
    print("--- Step 2: Creating & Signing Order ---")
    order = consumer.create_service_request(
        target_did=target_did,
        service="gpu_inference",
        max_price=0.01  # Consumer offers $0.01 (above minimum $0.005)
    )
    print(f"Offer Price: ${order['max_price']}")
    print(f"Digital Signature generated: {order['signature'][:30]}...\n")

    # 6. Provider processes order and confirms execution
    print("--- Step 3: Provider Processing & Verification ---")
    response = provider.process_incoming_request(order, min_acceptable_price=provider_min_price)
    
    print(f"Transaction Result Status: {response['status']}")
    if response["status"] == "ACCEPTED":
        consumer.budget -= response["settled_price"]
        provider.budget += response["settled_price"]
        print(f"Transaction ID: {response['transaction_id']}")
        print(f"Settled Price: ${response['settled_price']}")
        print(f"Updated Consumer Budget: ${consumer.budget:.3f}")
        print(f"Updated Provider Balance: ${provider.budget:.3f}")

    print("\n==================================================")
    print("   SUCCESSFULLY EXECUTED MACHINE-TO-MACHINE (M2M)  ")
    print("==================================================")