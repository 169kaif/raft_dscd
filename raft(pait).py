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
        
        #log will have list of tuples with (command, term)
        self.log = []
        self.commit_length = 0
        self.current_role = "follower"
        self.current_leader = None
        self.votes_received = set()

        self.peer_addresses = peer_addresses

        #init sent length
        self.sent_length = {}
        for node in peer_addresses.keys():
            self.sent_length[node] = 0

        #init acked length 
        self.acked_length = {}
        for node in peer_addresses.keys():
            self.acked_length[node] = 0

        #init database to store key value pairs
        self.database={}
        
        self.election_period_ms = randint(1000, 5000)
        self.rpc_period_ms = 3000
        self.last_heard = time.monotonic()
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

        message = request.Request
        req_action = message[:3]

        serveclient_reply = raft_pb2.ServeClientReply()

        #check requested action
        if (req_action == "SET"):

            if (self.current_role == "leader"):
                self.log.append((message, self.current_term))
                self.acked_length[node_id] = len(self.log)

                #replicate log to followers
                for follower in self.peer_addresses.keys():
                    self.replicateLog(follower)

                serveclient_reply.Data = ""
                serveclient_reply.LeaderID = self.current_leader
                serveclient_reply.Success = True

                return serveclient_reply
            else:
                serveclient_reply.Data = ""
                serveclient_reply.LeaderID = self.current_leader
                serveclient_reply.Success = False

                return serveclient_reply
            
        else:
            pass
            # if requested action is GET (LEADER LEASE IMPLEMENTATION NEEDED)
        
    def AppendEntries(self,prefixLen,LeaderCommit,suffix):

        if (len(suffix) > 0 and len(self.log)>prefixLen):
            index=min(len(self.log), prefixLen+len(suffix)) - 1
            
            if(self.log[index][-1]!=suffix[index-prefixLen][-1]):
                self.log=self.log[:prefixLen]

        if(prefixLen+len(suffix)>len(self.log)):
            for i in range(len(self.log)-prefixLen,len(suffix)):
                self.log.append(suffix[i])

        if (LeaderCommit > self.commit_length):

            for i in range(self.commit_length, LeaderCommit):

                #update database
                command = self.log[i]
                command = command.split()

                var_name = command[1]
                var_value = command[2]

                self.database[var_name] = var_value

            self.commit_length = LeaderCommit
         
    def ReplicateLogRequest(self, request, context):

        
        LeaderID = request.LeaderID
        Term = request.Term
        PrefixLength = request.PrefixLength
        PrefixTerm = request.PrefixTerm
        CommitLength = request.CommitLength
        Suffix = request.Suffix

        if (Term > self.current_term):
            self.current_term = Term
            self.voted_for = None
            #election timer canceled

        if (Term == self.current_term):
            self.current_role = "follower"
            self.current_leader = LeaderID

        #check if log is ok
        logok = ((len(self.log)>=PrefixLength) and (PrefixLength==0 or self.log[PrefixLength-1][-1]==PrefixTerm))

        #init replicate log response
        replicate_log_response = raft_pb2.ReplicateLogResponse()

        if (Term==self.current_term and logok):
            
            #call append entries
            ack=PrefixLength+len(Suffix)
            
            #populate log response
            replicate_log_response.NodeID = self.node_id
            replicate_log_response.CurrentTerm = self.current_leader
            replicate_log_response.ack = ack
            replicate_log_response.success = True

            #send log response
            return replicate_log_response

        else:

            #populate log response
            replicate_log_response.NodeID = self.node_id
            replicate_log_response.CurrentTerm = self.current_leader
            replicate_log_response.ack = 0
            replicate_log_response.Success = False

            #send diff log response
            return replicate_log_response

    def RequestVote(self, request, context):
        """invoked by node when in candidate set to request for votes
        """

        server_response=raft_pb2.RequestVoteResponse()

        candidateTerm = request.Term
        candidateID = request.CandidateID
        candidateLogLength = request.LastLogIndex
        candidateLastLogTerm = request.LastLogTerm
        
        # if node is in candidate state, upon receiving voteReq from
        # higher term, it transitions beack to the follower state
        if self.current_term < candidateTerm:
            self.current_term = candidateTerm
            self.current_role = "follower"
            self.voted_for = None

        lastTerm=0
        if (len(self.log) > 0):
            lastTerm = self.log[-1][-1]
        
        logok=(candidateLastLogTerm>lastTerm) or (candidateLastLogTerm==lastTerm and candidateLogLength>=len(self.log))
        if(candidateTerm==self.current_term and logok and (self.voted_for is None or self.voted_for==candidateID)):
            server_response.Term = self.current_term
            server_response.VoteGranted = True
            self.voted_for = candidateID
        
        else:
            server_response.Term=self.current_term
            server_response.VoteGranted=False   
        return server_response
    
    def set_election_timeout(self, timeout=None):
        # Reset this whenever previous timeout expires and starts a new election
        if timeout:
            self.election_timeout = timeout
        else:
            self.election_timeout = time.time() + randint(self.election_period_ms,
                                                          2*self.election_period_ms)/1000.0
    #method to request votes from all peers
    def request_vote(self):
        reply=""
        for id,address in self.peer_addresses:
            with grpc.insecure_channel(address) as channel:
                stub = raft_pb2.ServicesStub(channel)
                try:
                    req_msg = raft_pb2.RequestVoteArgs(Term = str(self.current_term), CandidateID = str(self.node_id), LastLogIndex = str(len(self.log)-1), LastLogTerm = self.log[-1])
                    response = stub.RequestVote(req_msg)
                    response_term = response.Term
                    response_vote = response.VoteGranted
                    if (self.current_role=="candidate" and response_term==self.current_term and response_vote==True):
                        self.votes_received.add(id)
                        if (len(self.votes_received) > (len(self.peer_addresses)+2)/2):
                            self.current_role = "leader"
                            self.current_leader = self.node_id
                            self.voted_for = None
                            reply="Success"
                            return reply
                    elif(response_term>self.current_term):
                        self.current_term = response_term
                        self.current_role = "follower"
                        self.voted_for = None
                        reply="Failed"
                        return reply
                except grpc.RpcError as e:
                    print(f"Failed to send Vote Request to {address}")

    def replicateLog(self,follower_id):
        prefixlen=self.sent_length[int(follower_id)-1]
        suffix=[self.log[i] for i in range(prefixlen,len(self.log))]
        sending_suffix=[i[0]+'|'+str(i[1]) for i in suffix]
        prefixterm=0
        if prefixlen>0:
            prefixterm=self.log[prefixlen-1][-1]
        with grpc.insecure_channel(self.peer_addresses[follower_id]) as channel:
                stub = raft_pb2.ServicesStub(channel)
                try:
                    req_msg = raft_pb2.ReplicateLogArgs(Term = self.current_term, LeaderID = self.current_leader, PrefixLength = prefixlen, PrefixTerm = prefixterm, CommitLength = self.commit_length, Suffix = sending_suffix)
                    response = stub.ReplicateLogRequest(req_msg)
                except grpc.RpcError as e:
                    print(f"Failed to send Vote Request to {follower_id}")

#this is "server" side basically

def nodeClient(Node):
    
    while True:

        #check current role
        if Node.current_role == "leader":

            #replicate log periodically
            current_time = time.monotonic()

            while(True):
                if ((time.monotonic() - current_time) > 100):
                    for i in Node.peer_addresses.keys():
                        Node.replicatelog(i)
                    current_time = time.monotonic()

        elif Node.current_role == "follower":
            start_time = time.monotonic()

            #check for rpc timeout
            while (time.monotonic() - start_time) < Node.rpc_period_ms:
                pass

            #transition to follower state when timeout
            Node.current_role = "candidate"

        elif Node.current_role == "candidate":

            #start election timer
            election_start_time = time.monotonic()
            
            #set bool variable to enter for the first time
            first_election = True
            
            while (True):
                
                #if higher term recieved, step down to follower state 
                #OR if election successful, transition to leader state
                #OR if some other node replies with a higher term
                if ((Node.current_role != "candidate") or (Node.votedFor != Node.node_id)):
                    break
                
                #if election times out, send message again
                if (first_election or (time.monotonic() - election_start_time > Node.elections_period_ms)):

                    if (first_election):
                        first_election = False
                    else:
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
                    
                    reply=Node.request_vote()
                    if(reply=="Success" and (time.monotonic() - election_start_time)< Node.elections_period_ms):
                        for id in peer_addresses.keys():
                            Node.sent_length[id]=len(Node.log)
                            Node.acked_length[id]=0
                            Node.replicateLog(id)
                        break


if __name__=="main":
    #node id
    node_id = sys.argv[1]
    port = sys.argv[2]
    peer_addresses = sys.argv[3:]
    node_RAFT = Node(node_id)
    #on 2 different threads to handle client and server
    
