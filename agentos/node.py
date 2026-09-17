import time
from typing import Dict, List, Optional
from .identity import AgentIdentity

class AgentNode:
    """
    Unified Node representation for creating Provider or Consumer agents easily.
    """
    def __init__(self, name: str, budget: float = 0.0):
        self.name = name
        self.identity = AgentIdentity()
        self.did = self.identity.did
        self.budget = budget

    def create_order(self, target_did: str, service: str, max_price: float) -> dict:
        """Helper method to construct and sign service purchase agreements."""
        timestamp = int(time.time())
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