import asyncio
import uuid
import random

class SwarmNode:
    def __init__(self, node_id=None):
        self.node_id = node_id or str(uuid.uuid4())
        self.peers = set()
        self.state = {}
        self.consensus_protocol = ConsensusProtocol(self)

    async def join_swarm(self, peers):
        self.peers.update(peers)
        await asyncio.gather(*[self.consensus_protocol.join_consensus(peer) for peer in peers])

    async def update_state(self, key, value):
        await self.consensus_protocol.propose_update(key, value)
        self.state[key] = value

    async def get_state(self, key):
        return self.state.get(key)

class ConsensusProtocol:
    def __init__(self, node):
        self.node = node
        self.quorum_size = max(1, len(self.node.peers) // 2)
        self.proposals = {}
        self.votes = {}

    async def join_consensus(self, peer_node):
        await self.sync_state(peer_node)
        self.node.peers.add(peer_node)

    async def sync_state(self, peer_node):
        for key, value in peer_node.state.items():
            if key not in self.node.state or self.node.state[key] != value:
                await self.propose_update(key, value)

    async def propose_update(self, key, value):
        proposal_id = str(uuid.uuid4())
        self.proposals[proposal_id] = (key, value)
        self.votes[proposal_id] = set()
        await self.gather_votes(proposal_id)
        if len(self.votes[proposal_id]) >= self.quorum_size:
            self.node.state[key] = value
            del self.proposals[proposal_id]
            del self.votes[proposal_id]

    async def gather_votes(self, proposal_id):
        tasks = []
        for peer in self.node.peers:
            tasks.append(self.vote_on_proposal(peer, proposal_id))
        await asyncio.gather(*tasks)

    async def vote_on_proposal(self, peer, proposal_id):
        key, value = self.proposals[proposal_id]
        if key in peer.state and peer.state[key] == value:
            self.votes[proposal_id].add(peer)
        else:
            self.votes[proposal_id].discard(peer)
