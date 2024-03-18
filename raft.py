from concurrent import futures
import grpc
import simple_raft_pb2
import simple_raft_pb2_grpc
import threading
import time
import sys

class RaftNode(simple_raft_pb2_grpc.RaftServicer):
    def __init__(self, node_id, peer_addresses):
        self.node_id = node_id
        self.peer_addresses = peer_addresses

    def Heartbeat(self, request, context):
        print(f"Heartbeat received from {request.nodeId}")
        return simple_raft_pb2.HeartbeatResponse(success=True)

    def SubmitCommand(self, request, context):
        print(f"Command received: {request.command}")
        # Simplified command processing logic
        return simple_raft_pb2.CommandResponse(success=True, result="Command processed")

    def start_server(self, port):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        simple_raft_pb2_grpc.add_RaftServicer_to_server(self, server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"Node {self.node_id} listening on port {port}")
        server.wait_for_termination()

    def send_heartbeat(self):
        for address in self.peer_addresses:
            with grpc.insecure_channel(address) as channel:
                stub = simple_raft_pb2_grpc.RaftStub(channel)
                try:
                    response = stub.Heartbeat(simple_raft_pb2.HeartbeatRequest(nodeId=self.node_id))
                    print(f"Heartbeat successfully sent to {address}")
                except grpc.RpcError as e:
                    print(f"Failed to send heartbeat to {address}: {e}")

    def start_heartbeating(self):
        while True:
            self.send_heartbeat()
            time.sleep(5)

def serve(node_id, port, peer_addresses):
    node = RaftNode(node_id, peer_addresses)
    threading.Thread(target=node.start_heartbeating, daemon=True).start()
    node.start_server(port)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python raft_node.py <node_id> <port> <peer_address_1> <peer_address_2> ...")
        sys.exit(1)
    node_id = sys.argv[1]
    port = sys.argv[2]
    peer_addresses = sys.argv[3:]
    serve(node_id, port, peer_addresses)
