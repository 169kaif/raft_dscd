import grpc
import raft_pb2
import raft_pb2_grpc

if __name__ == '__main__':

    #hard code peer addresses
    peer_addresses = {}
    
    #store current leader (initialized w/ 1)
    current_leader = 1

    while (True):
        req = input("Enter Request: ")

        while (True):
            with grpc.insecure_channel(peer_addresses[current_leader]) as channel:
                stub = raft_pb2_grpc.ServicesServicer(channel)
                req_message = raft_pb2.ServeClientArgs(Request = req)

                req_response = raft_pb2.ServeClient(req_message)

                recvd_data = req_response.Data
                recvd_LeaderID = req_response.LeaderID
                recvd_check = req_response.Success

                if (recvd_check):
                    print("Data retrieved Successfully...")
                    print(recvd_data)
                    break
                else:
                    print("Failure...Requesting Again...")
                    current_leader = recvd_LeaderID