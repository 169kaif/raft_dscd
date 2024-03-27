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

LEASE_TIME = 8

class Node(raft_pb2_grpc.ServicesServicer):
    
    def __init__(self, node_id, peer_addresses):
        self.node_id = node_id
        self.current_term = 0
        self.voted_for = None
        self.rpc_timeout_time=-1
        #log will have list of tuples with (command, term)
        self.log = []
        self.commit_length = 0
        self.current_role = "follower"
        self.current_leader = None
        self.votes_received = set()
        self.PrevLease=None
        self.peer_addresses = peer_addresses
        self.Haslease=False
        self.remaining_time=0
        self.Lease_time=8
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
        
        self.election_period_ms = randint(15, 20)
        self.rpc_period_ms = 10
        self.last_heard = time.monotonic()
        self.election_timeout=-1
        self.count_for_success_heartbeat=0

        node_log_location = f"node_id_{node_id}"

        if (os.path.exists(node_log_location) == False):
            
            #make dir
            os.mkdir(node_log_location)

            #change dir
            os.chdir(node_log_location)

            #init persistent files to dir
            with open("metadata.txt", "w") as f:
                f.write("commitLength: 0\n")
                f.write("Term: 0\n")
                f.write(f"NodeID: {node_id}\n")

            with open("logs.txt", "w") as f:
                pass

            with open("dump.txt", "w") as f:
                pass
            
        else:
            os.chdir(node_log_location)

            #read metadata
            with open("metadata.txt", "r") as f:
                metadata = f.readlines()

                self.commit_length = int(metadata[0].split(": ")[1])
                self.current_term = int(metadata[1].split(": ")[1])
                self.node_id = int(metadata[2].split(": ")[1])

            #restore log
            with open("logs.txt", "r") as f:
                logs=f.readlines()
                for line in logs:
                    line = line.split()
                    if line[0]=="SET":
                        self.database[line[1]]=line[2]
                        self.log.append((line[0:3], int(line[3])))
                    else:
                        self.log.append((line[0], int(line[1])))
                    

    def write_metadata(self):
        with open("metadata.txt", "w") as f:
            f.write(f"commitLength: {self.commit_length}\n")
            f.write(f"Term: {self.current_term}\n")
            f.write(f"NodeID: {node_id}\n")

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

        print(f"Node {self.node_id} (leader) received an {message} request.")
        with open("dump.txt", "a") as f:
            f.write(f"Node {self.node_id} (leader) received an {message} request.\n")

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

                print("Successfully SET the requested value...")

                return serveclient_reply
            else:
                serveclient_reply.Data = ""
                serveclient_reply.LeaderID = self.current_leader
                serveclient_reply.Success = False

                print("Unsuccessful SET of the requested value...")
                return serveclient_reply
            
        else:
            if (self.current_role == "leader"):
                if (self.Haslease):
                    print("Successfully replied to GET request...")
                    req_key = message.split()[1]
                    serveclient_reply.Data = self.database[req_key]
                    serveclient_reply.LeaderID = self.current_leader
                    serveclient_reply.Success = True

                    return serveclient_reply
                else:
                    print(f"Leader {self.node_id} does not have lease yet...")
                    serveclient_reply.Data = ""
                    serveclient_reply.LeaderID = self.current_leader
                    serveclient_reply.Success = False

                    return serveclient_reply
            else:

                print("Not the leader, replied w/ leader id...")
                serveclient_reply.Data = ""
                serveclient_reply.LeaderID = self.current_leader
                serveclient_reply.Success = False

                return serveclient_reply
        
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

                command = self.log[i][0]

                #append to persistent log.txt
                with open("logs.txt", "a") as f:
                    f.write(command+f" {self.current_term}\n")

                print(f"Node {self.node_id} (follower) committed the entry {command} to the state machine.")
                with open("dump.txt", "a") as f:
                    f.write(f"Node {self.node_id} (follower) committed the entry {command} to the state machine.\n")
                    
                #update database
                command = command.split()

                if (command[0] == "SET"):
                    var_name = command[1]
                    var_value = command[2]
                
                #check for SET COMMAND
                if (command[0] == "SET"):
                    self.database[var_name] = var_value

            self.commit_length = LeaderCommit
         
    def ReplicateLogRequest(self, request, context):

        self.rpc_timeout_time = time.monotonic()
        LeaderID = request.LeaderID
        Term = request.Term
        PrefixLength = request.PrefixLen
        PrefixTerm = request.PrefixTerm
        CommitLength = request.CommitLength
        Suffix = request.Suffix
        Suffix_list = list(Suffix)
        Suffix=[(x.split('|')[0],int(x.split('|')[1])) for x in Suffix_list]
        self.PrevLease=request.leaseReminder

        if (Term > self.current_term):
            self.current_term = Term
            self.voted_for = None
            #election timer canceled

        if (Term == self.current_term):
            self.current_role = "follower"
            self.current_leader = LeaderID

        #rewrite metadata to persistent memory
        self.write_metadata()

        print("The current term is: ", self.current_term)
        print("The log is: ", self.log)
        print("The suffix is: ", Suffix)
        print("Checking if log is ok...")

        print("the length of the log is: ", len(self.log))
        print("the prefix length is: ", PrefixLength)
        print("the last term of the prefix is: ", PrefixTerm)
        if (PrefixLength > 0 and len(self.log) >= PrefixLength):
            print("the last term of the log is: ", self.log[PrefixLength-1][-1])

        #check if log is ok
        logok = ((len(self.log)>=PrefixLength) and (PrefixLength==0 or self.log[PrefixLength-1][-1]==PrefixTerm))

        print("Log is ok: ", logok)

        #init replicate log response
        replicate_log_response = raft_pb2.ReplicateLogResponse()

        if (Term==self.current_term and logok):
            
            print(f"Node {self.node_id} accepted AppendEntries RPC from {self.current_leader}.")
            with open("dump.txt", "a") as f:
                f.write(f"Node {self.node_id} accepted AppendEntries RPC from {self.current_leader}.\n")

            #call append entries
            self.AppendEntries(PrefixLength, CommitLength, Suffix)
            ack=PrefixLength+len(Suffix)

            #populate log response
            replicate_log_response.NodeID = self.node_id
            replicate_log_response.CurrentTerm = self.current_leader
            replicate_log_response.ack = ack
            replicate_log_response.success = True

            #send log response
            return replicate_log_response

        else:

            print(f"Node {self.node_id} rejected AppendEntries RPC from {self.current_leader}.")
            with open("dump.txt", "a") as f:
                f.write(f"Node {self.node_id} rejected AppendEntries RPC from {self.current_leader}.\n")

            #populate log response
            replicate_log_response.NodeID = self.node_id
            replicate_log_response.CurrentTerm = self.current_leader
            replicate_log_response.ack = 0
            replicate_log_response.success = False

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

        #rewrite metadata
        self.write_metadata()
        
        logok=(candidateLastLogTerm>lastTerm) or (candidateLastLogTerm==lastTerm and candidateLogLength>=len(self.log))
        if(candidateTerm==self.current_term and logok and (self.voted_for is None or self.voted_for==candidateID)):
            server_response.Term = self.current_term
            server_response.VoteGranted = True
            self.voted_for = candidateID

            print(f"Vote granted for Node {candidateID} in term {self.current_term}")
            with open("dump.txt", "a") as f:
                f.write(f"Vote granted for Node {candidateID} in term {self.current_term}\n")
        
        else:
            server_response.Term=self.current_term
            server_response.VoteGranted=False   

            print(f"Vote denied for Node {candidateID} in term {self.current_term}")
            with open("dump.txt", "a") as f:
                f.write(f"Vote denied for Node {candidateID} in term {self.current_term}\n")

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
        for id,address in self.peer_addresses.items():
            with grpc.insecure_channel(address) as channel:
                stub = raft_pb2_grpc.ServicesStub(channel)
                try:
                    if(len(self.log)==0):
                        req_msg = raft_pb2.RequestVoteArgs(Term = self.current_term, CandidateID = self.node_id, LastLogIndex = len(self.log), LastLogTerm =0)
                    else:
                        req_msg = raft_pb2.RequestVoteArgs(Term = self.current_term, CandidateID = self.node_id, LastLogIndex = len(self.log), LastLogTerm = self.log[-1][-1])
                    
                    response = stub.RequestVote(req_msg)
                    response_term = response.Term
                    response_vote = response.VoteGranted

                    if (self.current_role=="candidate" and response_term==self.current_term and response_vote==True):
                        self.votes_received.add(id)
                        if ((len(self.votes_received)) >=3):#hardcode
                            self.current_role = "leader"

                            #must be committed to persistent log
                            # self.log.append(("NO-OP", self.current_term))

                            if (self.current_role == "leader"):
                                print(f'Node {self.node_id} became the leader for term {self.current_term}')
                                with open('dump.txt','a') as f:
                                    f.write(f'Node {self.node_id} became the leader for term {self.current_term}\n')

                            self.current_leader = self.node_id
                            # self.voted_for = None
                            reply="Success"

                            #write metadata
                            self.write_metadata()
                            return reply
                        
                    elif(response_term>self.current_term):
                        self.current_term = response_term
                        self.current_role = "follower"
                        
                        self.voted_for = None
                        reply="Failed"
                        
                        #write metadata
                        self.write_metadata()
                        return reply
                    
                except grpc.RpcError as e:
                    print(f"Error occurred while sending RPC to Node {id}.")
                    with open('dump.txt','a') as f:
                        f.write(f"Error occurred while sending RPC to Node {id}.\n")

    def CommitLogEntries(self):

        while self.commit_length<len(self.log):
            
            acks=0

            for id in self.peer_addresses.keys():
                if self.acked_length[id]>self.commit_length:
                    acks += 1

            if acks>=2:#hardcode

                command = self.log[self.commit_length][0]

                print(f"Node {self.node_id} (leader) committed the entry {command} to the state machine.")
                with open("dump.txt", "a") as f:
                    f.write(f"Node {self.node_id} (leader) committed the entry {command} to the state machine.")
                
                #append to persistent log
                with open("logs.txt", "a") as f:
                    f.write(command + f" {self.current_term}\n")

                command = command.split()

                if (command[0] == "SET"):
                    var_name = command[1]
                    var_value = command[2]

                if (command[0] == "SET"):
                    self.database[var_name] = var_value

                self.commit_length+=1
            else:
                break                

    def replicateLog(self,follower_id):
        prefixlen=self.sent_length[follower_id]
        suffix=[self.log[i] for i in range(prefixlen,len(self.log))]
        sending_suffix=[i[0]+'|'+str(i[1]) for i in suffix]

        prefixterm=0
        if prefixlen>0:
            prefixterm=self.log[prefixlen-1][-1]

        with grpc.insecure_channel(self.peer_addresses[follower_id]) as channel:
                stub = raft_pb2_grpc.ServicesStub(channel)
                try:

                    req_msg = raft_pb2.ReplicateLogArgs()
                    req_msg.Term = self.current_term
                    req_msg.LeaderID = self.current_leader
                    req_msg.PrefixLen = prefixlen
                    req_msg.PrefixTerm = prefixterm
                    req_msg.CommitLength = self.commit_length
                    req_msg.Suffix.extend(sending_suffix)
                    req_msg.leaseReminder=self.remaining_time 

                    # raft_pb2.ReplicateLogArgs(Term = self.current_term, LeaderID = self.current_leader, PrefixLen = prefixlen, PrefixTerm = prefixterm, CommitLength = self.commit_length, Suffix = sending_suffix,leaseReminder=self.remaining_time)

                    response = stub.ReplicateLogRequest(req_msg)

                    # message ReplicateLogResponse{
                    # int32 NodeID = 1;
                    # int32 CurrentTerm = 2;
                    # int32 ack = 3;
                    # bool success = 4;

                    response_current_term = response.CurrentTerm
                    response_ack = response.ack
                    response_success = response.success

                    if(response_success):
                        self.count_for_success_heartbeat+=1

                    if (response_current_term == self.current_term and self.current_role=="leader"):
                        if (response_success and response_ack >= self.acked_length[follower_id]):
                            self.sent_length[follower_id] = response_ack
                            self.acked_length[follower_id] = response_ack
                            self.CommitLogEntries()

                        elif (self.sent_length[follower_id] > 0):
                            #log mismatch, so decrease sent length by 1
                            print(f"log mismatch for {follower_id}, length of follower log is: {self.sent_length[follower_id]}")
                            self.sent_length[follower_id] -= 1
                            self.replicateLog(follower_id)

                    elif (response_current_term > self.current_term):
                        self.current_term = response_current_term
                        self.current_role = "follower"
                        self.voted_for = None

                    #write metadata
                    self.write_metadata()

                except grpc.RpcError as e:
                    print(f"Error occurred while sending RPC to Node {follower_id}.")
                    with open('dump.txt','a') as f:
                        f.write(f"Error occurred while sending RPC to Node {follower_id}.\n")


def nodeClient(Node):

    while True:

        print(Node.log)
        #check current role
        if Node.current_role == "leader":
            #replicate log periodically
            current_time = time.monotonic()
            if(Node.PrevLease is None):
                pass
            else:
                print(f"New Leader waiting for Old Leader Lease to timeout.")
                while((time.monotonic()-current_time)-Node.PrevLease>0):
                    break

            Node.Haslease=True
            if (Node.Haslease):
                print(f"Leader {Node.node_id} has lease.")
                Node.log.append(("NO-OP", Node.current_term))
                with open("dump.txt", "a") as f:
                    f.write(f"Leader {Node.node_id} has lease.\n")

            while(True):
    
                if(time.monotonic()-current_time>Node.Lease_time):

                    print(f"Leader {Node.node_id} lease Renewal failed...stepping down")
                    with open("dump.txt", "a") as f:
                        f.write(f"Leader {Node.node_id} lease Renewal failed...stepping down\n")
                        Node.Haslease=False

                    Node.current_role = "follower"

                    print(f"{Node.node_id} Stepping down")
                    with open("dump.txt", "a") as f:
                        f.write(f"{Node.node_id} Stepping down")
                    
                    Node.count_for_success_heartbeat=0
                    break

                #sending heartbeat and renewing lease
                if ((time.monotonic() - current_time) >=7):
                
                    print(f"Leader {Node.node_id} sending heartbeat and renewing lease.")
                    with open("dump.txt", "a") as f:
                        f.write(f"Leader {Node.node_id} sending heartbeat and renewing lease.\n")
                    
                    for i in Node.peer_addresses.keys():
                        remaining=time.monotonic()-current_time-Node.Lease_time
                        Node.remaining_time=remaining
                        Node.replicateLog(i)
                    if(Node.count_for_success_heartbeat>=2):#hardcode
                        Node.count_for_success_heartbeat=0
                        Node.Lease_time=LEASE_TIME
                    current_time = time.monotonic()


        elif Node.current_role == "follower":
            Node.rpc_timeout_time = time.monotonic()
            print(f"Node {Node.node_id} is in follower state.")
            #check for rpc timeout
            while (time.monotonic() - Node.rpc_timeout_time) < Node.rpc_period_ms:
                pass

            #transition to candidate state when timeout
            print(f"Node {Node.node_id} election timer timed out, Starting election")
            with open("dump.txt", "a") as f:
                f.write(f"Node {Node.node_id} election timer timed out, Starting election\n")
            
            Node.current_role = "candidate"

        elif Node.current_role == "candidate":
            print(f"Node {Node.node_id} is in candidate state.")

            #start election timer
            election_start_time = time.monotonic()

            #set voted for to itself
            Node.voted_for = Node.node_id
            
            #set bool variable to enter for the first time
            first_election = True
            
            while (True):
                
                #if higher term recieved, step down to follower state 
                #OR if election successful, transition to leader state
                #OR if some other node replies with a higher term
                        
                if ((Node.current_role != "candidate") or (Node.voted_for != Node.node_id)):
                    break
                
                #if election times out, send message again
                if (first_election or (time.monotonic() - election_start_time > Node.election_period_ms)):

                    if (first_election):
                        first_election = False
                    else:
                        election_start_time = time.monotonic()

                    #increment current term
                    Node.current_term += 1

                    #vote for self, need to, WRITE TO LOG AS WELL 
                    Node.voted_for = Node.node_id

                    #clear and add vote to votes_received
                    Node.votes_received.clear()
                    Node.votes_received.add(Node.node_id)

                    #check last term
                    Node.last_term = 0
                    if (len(Node.log) > 0):
                        Node.last_term = Node.log[-1][-1]
                
                    #request vote from all nodes inside a while loop
                    
                    reply=Node.request_vote()
                    if(reply=="Success"):
                        for id in peer_addresses.keys():
                            Node.sent_length[id]=len(Node.log)
                            Node.acked_length[id]=0
                            Node.replicateLog(id)
                        break


if __name__ == '__main__':

    node_id = 1
    port = 5056
    peer_addresses = {2:"localhost:5057", 3:"localhost:5058", 4:"localhost:5059", 5:"localhost:5060"}
    node = Node(node_id, peer_addresses)

    #spawn 2 different threads to handle client and serve
    client_thread = threading.Thread(target=nodeClient, args=(node,))
    client_thread.start()
    node.startServer(port)
    