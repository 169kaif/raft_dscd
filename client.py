import grpc
import raft_pb2
import raft_pb2_grpc

if __name__ == '__main__':

    #hard code peer addresses
    peer_addresses = {1:"localhost:5056", 2:"localhost:5057", 3:"localhost:5058", 4:"localhost:5059", 5:"localhost:5060"}
    
    #store current leader (init w/ 1)
    current_leader = 3
    check=0

    while (True):
        req = input("Enter Request: ")

        while (True):

            print("The current leader is: ", current_leader)

            try:
            
                with grpc.insecure_channel(peer_addresses[current_leader]) as channel:
                    stub = raft_pb2_grpc.ServicesStub(channel)
                    print(type(req), req)
                    req_message = raft_pb2.ServeClientArgs(Request = req)

                    req_response = stub.ServeClient(req_message)

                    recvd_data = req_response.Data
                    recvd_LeaderID = req_response.LeaderID
                    recvd_check = req_response.Success

                    if (recvd_check):
                        print("Operation Successful...")
                        print(recvd_data)
                        check=0
                        break
                    else:
                        print("Failure...Requesting Again...")
                        current_leader = recvd_LeaderID
                    

            except:
                check+=1
                if(check==5):
                     break
                print("Node Down...Requesting Again From Different Node...")
                current_leader = (current_leader % 5) + 1
                continue
        if(check==5):
             break