import time
import httpx
from identity import AgentIdentity

REGISTRY_URL = "http://127.0.0.1:8000"

def run_consumer():
    # 1. Initialize Consumer Identity
    consumer_identity = AgentIdentity()
    print(f"[CONSUMER ONLINE] DID: {consumer_identity.did}")

    # 2. Discover Provider via Registry HTTP API
    print("\n--- 1. Querying Registry for 'gpu_inference' ---")
    try:
        res = httpx.get(f"{REGISTRY_URL}/discover", params={"capability": "gpu_inference"})
        data = res.json()
    except Exception as e:
        print(f"[ERROR] Failed to connect to Registry Server: {e}")
        return

    if data.get("count", 0) == 0:
        print("[WARNING] No active providers found in the network!")
        return

    provider_info = data["agents"][0]
    provider_did = provider_info["did"]
    provider_endpoint = provider_info["endpoint"]
    print(f"Discovered Provider DID: {provider_did}")
    print(f"Provider Endpoint: {provider_endpoint}")

    # 3. Build and Sign Fair Agreement Proposal
    print("\n--- 2. Building & Signing HTTP Order ---")
    timestamp = int(time.time())
    
    # Setting an attractive offer price ($0.02) to guarantee AI acceptance
    max_price = 0.02  
    service = "gpu_inference"
    payload_string = f"BUY_SERVICE:{consumer_identity.did}:{provider_did}:{service}:{max_price}:{timestamp}"
    signature = consumer_identity.sign_message(payload_string)

    order_payload = {
        "buyer_did": consumer_identity.did,
        "target_did": provider_did,
        "service": service,
        "max_price": max_price,
        "timestamp": timestamp,
        "payload_string": payload_string,
        "signature": signature
    }

    # 4. Dispatch Order Directly to Provider Endpoint
    print("\n--- 3. Sending Order to Provider Endpoint ---")
    try:
        exec_res = httpx.post(f"{provider_endpoint}/execute", json=order_payload)
        print(f"Response Status Code: {exec_res.status_code}")
        print(f"Response Payload: {exec_res.json()}")
    except Exception as e:
        print(f"[ERROR] Failed to communicate with Provider Node: {e}")

if __name__ == "__main__":
    run_consumer()