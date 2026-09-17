from concurrent import futures
import grpc
from agentos import agentos_pb2, agentos_pb2_grpc

class AgentRegistryServicer(agentos_pb2_grpc.AgentRegistryServicer):
    def __init__(self):
        self.registered_agents = []

    def RegisterAgent(self, request, context):
        agent_data = {
            "did": request.did,
            "capabilities": list(request.capabilities),
            "endpoint": request.endpoint
        }
        self.registered_agents.append(agent_data)
        print(f"[gRPC REGISTRY] Registered Agent: {request.did[:25]}... at {request.endpoint}")
        return agentos_pb2.RegisterResponse(success=True, message="Agent registered successfully")

    def DiscoverAgents(self, request, context):
        matching = [
            agentos_pb2.AgentMetadata(
                did=a["did"],
                capabilities=a["capabilities"],
                endpoint=a["endpoint"]
            )
            for a in self.registered_agents
            if request.capability in a["capabilities"]
        ]
        return agentos_pb2.DiscoverResponse(agents=matching)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    agentos_pb2_grpc.add_AgentRegistryServicer_to_server(AgentRegistryServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("[gRPC REGISTRY SERVER] Running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()