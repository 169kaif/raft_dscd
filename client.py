import grpc
import simple_raft_pb2
import simple_raft_pb2_grpc

def send_command(target, command):
    with grpc.insecure_channel(target) as channel:
        stub = simple_raft_pb2_grpc.RaftStub(channel)
        response = stub.SubmitCommand(simple_raft_pb2.CommandRequest(command=command))
        print(f"Command response: {response.result}")

if __name__ == '__main__':
    target = "localhost:50051"  # Target node address
    command = "Store this data"
    send_command(target, command)
