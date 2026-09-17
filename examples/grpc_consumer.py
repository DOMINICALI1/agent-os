import grpc
from cryptography.hazmat.primitives.asymmetric import ed25519

from agentos import agentos_pb2
from agentos import agentos_pb2_grpc

def run():
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_bytes = private_key.public_key().public_bytes_raw()
    my_did = f"did:agentos:{public_bytes.hex()[:16]}"

    channel = grpc.insecure_channel("localhost:50052")
    stub = agentos_pb2_grpc.AgentServiceStub(channel)

    handshake_res = stub.Handshake(agentos_pb2.HandshakeRequest(
        consumer_did=my_did,
        capability_required="gpu_inference"
    ))
    print(f"[HANDSHAKE] Provider DID: {handshake_res.provider_did}")

    max_budget = 15.0
    current_offer = 5.0
    round_num = 1
    agreed = False
    final_price = 0.0

    while round_num <= 3:
        req = agentos_pb2.NegotiateRequest(
            consumer_did=my_did,
            capability="gpu_inference",
            offered_price=current_offer,
            round=round_num
        )
        res = stub.Negotiate(req)

        if res.status == agentos_pb2.NegotiateResponse.ACCEPTED:
            print(f"[NEGOTIATION] Accepted at ${current_offer} in round {round_num}.")
            agreed = True
            final_price = current_offer
            break
        elif res.status == agentos_pb2.NegotiateResponse.COUNTER_OFFER:
            print(f"[ROUND {round_num}] Proposed ${current_offer} | Provider counter: ${res.counter_price}")
            current_offer = round((current_offer + res.counter_price) / 2, 2)
            if current_offer > max_budget:
                print("[NEGOTIATION] Counter offer exceeds budget threshold.")
                break
            round_num += 1
        else:
            print("[NEGOTIATION] Rejected by provider.")
            break

    if agreed:
        def generate_chunks():
            for i in range(1, 4):
                yield agentos_pb2.DataChunk(
                    session_id="SESSION_NEGOTIATED_01",
                    sequence_number=i,
                    payload=f"Payload Data Chunk #{i}".encode("utf-8")
                )

        responses = stub.StreamTaskData(generate_chunks())
        for r in responses:
            print(f"[STREAM ACK] Session: {r.session_id} | Chunk #{r.sequence_number} | Status: {r.status_message}")

if __name__ == "__main__":
    run()