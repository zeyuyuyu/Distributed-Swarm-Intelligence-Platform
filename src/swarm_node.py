import random
import time
from typing import List, Tuple

class SwarmNode:
    def __init__(self, node_id: str, neighbors: List[str]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.state = 'IDLE'
        self.leader = None
        self.term = 0
        self.votes = 0

    def run(self):
        while True:
            if self.state == 'IDLE':
                self.check_for_election()
            elif self.state == 'CANDIDATE':
                self.start_election()
            elif self.state == 'FOLLOWER':
                self.follow_leader()
            elif self.state == 'LEADER':
                self.lead_swarm()
            time.sleep(random.uniform(0.1, 0.5))

    def check_for_election(self):
        if random.random() < 0.1:
            self.state = 'CANDIDATE'
            self.term += 1
            self.votes = 1

    def start_election(self):
        print(f'Node {self.node_id} started election for term {self.term}')
        for neighbor in self.neighbors:
            self.send_vote_request(neighbor)
        self.wait_for_votes()

    def send_vote_request(self, neighbor: str):
        # Simulate sending a vote request to a neighbor
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.8:
            self.receive_vote(neighbor)

    def receive_vote(self, voter: str):
        self.votes += 1
        if self.votes > len(self.neighbors) // 2:
            self.state = 'LEADER'
            self.leader = self.node_id
            print(f'Node {self.node_id} became the leader for term {self.term}')
            self.broadcast_heartbeat()

    def wait_for_votes(self):
        time.sleep(random.uniform(1, 3))
        if self.votes <= len(self.neighbors) // 2:
            self.state = 'FOLLOWER'
            self.leader = next((n for n in self.neighbors if n != self.node_id), None)
            print(f'Node {self.node_id} became a follower in term {self.term}')

    def follow_leader(self):
        # Simulate following the leader
        time.sleep(random.uniform(0.5, 1.5))
        if random.random() < 0.1:
            self.check_for_election()

    def lead_swarm(self):
        self.broadcast_heartbeat()
        if random.random() < 0.1:
            self.handle_follower_failure()

    def broadcast_heartbeat(self):
        # Simulate broadcasting a heartbeat to all neighbors
        for neighbor in self.neighbors:
            self.send_heartbeat(neighbor)

    def send_heartbeat(self, neighbor: str):
        # Simulate sending a heartbeat to a neighbor
        time.sleep(random.uniform(0.1, 0.5))

    def handle_follower_failure(self):
        # Simulate handling a follower failure
        failed_follower = random.choice(self.neighbors)
        print(f'Node {self.node_id} detected failure of follower {failed_follower}')
        self.neighbors.remove(failed_follower)
        self.broadcast_updated_topology()

    def broadcast_updated_topology(self):
        # Simulate broadcasting the updated topology to all neighbors
        for neighbor in self.neighbors:
            self.send_topology_update(neighbor)

    def send_topology_update(self, neighbor: str):
        # Simulate sending a topology update to a neighbor
        time.sleep(random.uniform(0.1, 0.5))
