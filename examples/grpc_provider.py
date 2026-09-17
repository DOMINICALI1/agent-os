import concurrent.futures
import time
import grpc
from cryptography.hazmat.primitives.asymmetric import ed25519

import agentos_pb2
import agentos_pb2_grpc

class AgentServiceProvider(agentos_pb2_grpc.AgentServiceServicer):
    def __init__(self):
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_bytes = self.private_key.public_key().public_bytes_raw()
        self.did = f"did:agentos:{self.public_bytes.hex()[:16]}"
        self.min_price = 1.0
        self.target_price = 12.0

    def Handshake(self, request, context):
        return agentos_pb2.HandshakeResponse(
            accepted=True,
            provider_did=self.did,
            message="Handshake accepted."
        )

    def Negotiate(self, request, context):
        offered = request.offered_price
        round_num = request.round

        if offered >= self.target_price:
            return agentos_pb2.NegotiateResponse(
                status=agentos_pb2.NegotiateResponse.ACCEPTED,
                counter_price=offered,
                ai_reasoning="Offer meets target price."
            )

        if round_num >= 3 and offered >= self.min_price:
            return agentos_pb2.NegotiateResponse(
                status=agentos_pb2.NegotiateResponse.ACCEPTED,
                counter_price=offered,
                ai_reasoning="Final round agreement reached."
            )

        if offered < self.min_price:
            return agentos_pb2.NegotiateResponse(
                status=agentos_pb2.NegotiateResponse.REJECTED,
                counter_price=0.0,
                ai_reasoning="Offer is below minimum threshold."
            )

        step = (self.target_price - self.min_price) / 3
        counter_price = round(self.target_price - (round_num * step), 2)
        counter_price = max(counter_price, self.min_price)

        return agentos_pb2.NegotiateResponse(
            status=agentos_pb2.NegotiateResponse.COUNTER_OFFER,
            counter_price=counter_price,
            ai_reasoning=f"Counter offer calculated for round {round_num}."
        )

    def StreamTaskData(self, request_iterator, context):
        for chunk in request_iterator:
            yield agentos_pb2.DataChunkResponse(
                session_id=chunk.session_id,
                sequence_number=chunk.sequence_number,
                acknowledged=True,
                status_message="PROCESSED"
            )

def serve():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    agentos_pb2_grpc.add_AgentServiceServicer_to_server(AgentServiceProvider(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("[PROVIDER ONLINE] Port: 50052")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()