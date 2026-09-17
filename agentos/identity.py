import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class AgentIdentity:
    """
    Manages cryptographic identity (Ed25519) and signs messages 
    to prevent tampering within the Agent OS network.
    """
    def __init__(self):
        # Generate private and public keypair for the agent
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()
        
        # Derive the unique Decentralized Identifier (DID)
        self.did = self._generate_did()

    def _generate_did(self) -> str:
        """Generates a globally unique DID based on the public key fingerprint."""
        public_bytes = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        # Encode public key in Base64 and format according to DID specification
        encoded_key = base64.b64encode(public_bytes).decode('utf-8').rstrip('=')
        return f"did:agentos:{encoded_key}"

    def sign_message(self, message: str) -> str:
        """Signs a text payload using the agent's private key."""
        signature = self._private_key.sign(message.encode('utf-8'))
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_signature(public_did: str, message: str, signature_b64: str) -> bool:
        """
        Static method to verify if a message was signed by the holder of the DID.
        """
        try:
            # Extract raw public key from the DID string
            raw_key_b64 = public_did.replace("did:agentos:", "")
            
            # Re-apply Base64 padding if necessary
            padding = '=' * (4 - (len(raw_key_b64) % 4))
            public_bytes = base64.b64decode(raw_key_b64 + padding)
            
            # Reconstruct the public key and verify signature
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_bytes)
            signature = base64.b64decode(signature_b64)
            
            public_key.verify(signature, message.encode('utf-8'))
            return True
        except Exception:
            return False


# --- Local testing and verification ---
if __name__ == "__main__":
    print("--- 1. Generating New Agent Identity ---")
    agent_a = AgentIdentity()
    print(f"Agent A DID: {agent_a.did}\n")

    print("--- 2. Signing Service Request Payload ---")
    data_payload = "REQUEST_GPU_INFERENCE:model=qwen2.5:price=0.002"
    signature = agent_a.sign_message(data_payload)
    print(f"Message Payload: {data_payload}")
    print(f"Digital Signature: {signature}\n")

    print("--- 3. Verifying Signature ---")
    is_valid = AgentIdentity.verify_signature(agent_a.did, data_payload, signature)
    print(f"Is signature valid? -> {is_valid}")

    # Testing tampered data detection
    tampered_payload = "REQUEST_GPU_INFERENCE:model=qwen2.5:price=0.0001"
    is_tampered_valid = AgentIdentity.verify_signature(agent_a.did, tampered_payload, signature)
    print(f"Is tampered message valid? -> {is_tampered_valid}")