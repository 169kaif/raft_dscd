#make imports
import os
import sys
from random import randint
import time
import threading
from concurrent import futures
import grpc
import raft_pb2
import raft_pb2_grpc


class Node(raft_pb2_grpc.ServicesServicer):
    def __init__(self, node_id, peer_addresses):
        self.node_id = node_id
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_length = 0
        self.current_role = "follower"
        self.current_leader = None
        self.votes_received = set()
        self.sent_length = []
        self.acked_length = []
        self.database={}
        self.peer_addresses = peer_addresses

        self.election_period_ms = randint(1000, 5000)
        self.rpc_period_ms = 3000
        self.election_timeout=-1

        node_log_location = f"node_id_{node_id}"

        if (os.exists(node_log_location) == False):
            
            #make dir
            os.mkdir(node_log_location)

            #change dir
            os.chdir(node_log_location)

            #init persistent files to dir
            with open("metadata.txt", "w") as f:
                f.write("commitLength: 0")
                f.write("Term: 0")
                f.write(f"NodeID: {node_id}")

            with open("logs.txt", "w") as f:
                f.write(f"NO-OP {self.current_term}")

            with open("dump.txt", "w") as f:
                pass
        # else:
            ##do restoration

    

    def startServer(self, port):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
        raft_pb2_grpc.add_ServicesServicer_to_server(self,server)
        server.add_insecure_port(f'[::]:{port}')
        server.start()
        print(f"Node {self.node_id} listening on port {port}")
        server.wait_for_termination()

    def ServeClient(self, request, context):
        """client -> requests certain data from the server
        server -> replies w/ data, leader id, bool variable depicting success or failure

        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AppendEntries(self, request, context):
        """invoked by leader to replicate log entries and to send heartbeats
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestVote(self, request, context):
        """invoked by node when in candidate set to request for votes
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')
    
    def set_election_timeout(self, timeout=None):
        # Reset this whenever previous timeout expires and starts a new election
        if timeout:
            self.election_timeout = timeout
        else:
            self.election_timeout = time.time() + randint(self.election_period_ms,
                                                          2*self.election_period_ms)/1000.0
    #method to request votes from all peers
    
#this is "server" side basically

def nodeCLient(Node):
    while True:

        #check current role
        if Node.current_role == "leader":
            pass

        elif Node.current_role == "follower":
            start_time = time.monotonic()

            #check for rpc timeout
            while (time.monotonic() - start_time)*1000 < Node.rpc_period_ms:
                pass

            #transition to follower state when timeout
            Node.current_role = "candidate"

        elif Node.current_role == "candidate":

            #start election timer
            election_start_time = time.monotonic()

            #increment current term
            Node.current_term += 1

            #vote for self, need to, WRITE TO LOG AS WELL 
            Node.votedFor = Node.node_id

            #clear and add vote to votes_received
            Node.votes_received.clear()
            Node.votes_received.add(Node.node_id)

            #check last term
            Node.last_term = None
            if (len(Node.log) > 0):
                Node.last_term = Node.log[-1]

            #request vote from all nodes inside a while loop
            while (True):

                #if election times out, send message again
                if ((time.monotonic() - election_start_time)*1000 > Node.elections_period_ms):
                    threading.Thread(target=Node.request_vote, daemon=True).start()


                    #NEED TO WORK ON IF CONSENSUS RECEIVED, MOVE TO LEADER STATE
                    #NEED TO MODIFY METHOD IN NODE CLASS TO JUDGE CONSENSUS
                    #IF HIGHER TERM RECEIVED, STEP DOWN TO FOLLOWER STATE


if __name__=="main":
    #parse through terminal arguments
    node_id = sys.argv[1]
    port = sys.argv[2]
    peer_addresses = sys.argv[3:]
    node_RAFT = Node(node_id)
    #on 2 different threads to handle client and server
    
