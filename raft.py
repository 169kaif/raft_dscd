#make imports
import os
import sys
from random import randint
import time


class Node:
    def __init__(self, node_id):
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

        self.election_period_ms = randint(1000, 5000)
        self.rpc_period_ms = 3000
        # self.election_timeout = -1

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

        #start election timeout
        self.election_timeout = time.monotonic() + self.election_period_ms
        

def nodeServe(Node):
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
            
            


if __name__=="main":
    #parse through terminal arguments
    node_id = sys.argv[1]
    node = Node(node_id)
    nodeServe(node)
