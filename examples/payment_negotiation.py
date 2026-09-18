import os
import json
from agentos_net.sdk import AgentOSClient, ProtocolConfig
from agentos_net.crypto import KeysManager

# Initialize Cryptographic Identities for Both Agents
provider_keys = KeysManager.generate_keypair()
consumer_keys = KeysManager.generate_keypair()

provider_did = f"did:agentos:{provider_keys.public_key_hex[:16]}"
consumer_did = f"did:agentos:{consumer_keys.public_key_hex[:16]}"

class AgentPaymentLayer:
    def __init__(self, payment_type="crypto", wallet_address=None, stripe_account_id=None):
        self.payment_type = payment_type
        self.wallet_address = wallet_address
        self.stripe_account_id = stripe_account_id

    def create_payment_terms(self, price_usd, currency="USDC"):
        if self.payment_type == "crypto":
            return {
                "payment_mode": "crypto_escrow",
                "amount": price_usd,
                "currency": currency,
                "pay_to_address": self.wallet_address,
                "network": "solana"  # Or ethereum / base
            }
        elif self.payment_type == "stripe":
            return {
                "payment_mode": "stripe_fiat",
                "amount": price_usd,
                "currency": "USD",
                "stripe_account": self.stripe_account_id
            }

def run_payment_demo():
    # 1. Setup Payment Configuration for Provider
    provider_payment = AgentPaymentLayer(
        payment_type="crypto",
        wallet_address="0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
    )

    # 2. Define Negotiated Payload with Payment Requirements
    proposal_terms = provider_payment.create_payment_terms(price_usd=25.0, currency="USDC")
    
    negotiation_payload = {
        "task": "dataset_sentiment_analysis",
        "service_level_agreement": "sub_500ms_latency",
        "payment_requirements": proposal_terms
    }

    print(f"[Provider Node] Initiating Service Offer with DID: {provider_did}")
    print(f"[Provider Terms] Generated Payment Structure:\n{json.dumps(negotiation_payload, indent=2)}")

    # 3. Simulate Consumer Verification and Handshake
    print(f"\n[Consumer Node] Verifying Terms with DID: {consumer_did}")
    if proposal_terms["payment_mode"] == "crypto_escrow":
        print(f"[Payment Engine] Locking {proposal_terms['amount']} {proposal_terms['currency']} in Escrow Contract...")
        print(f"[Payment Engine] Escrow Lock Confirmed for Target: {proposal_terms['pay_to_address']}")
    
    print("[AgentOS Protocol] Execution Auth Token Issued. Ready for gRPC stream.")

if __name__ == "__main__":
    run_payment_demo()