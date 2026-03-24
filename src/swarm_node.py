import asyncio
import random
from typing import List

class SwarmNode:
    def __init__(self, node_id: str, neighbors: List['SwarmNode']):
        self.node_id = node_id
        self.neighbors = neighbors
        self.state = 'idle'
        self.task = None

    async def run(self):
        while True:
            if self.state == 'idle':
                await self.participate_in_consensus()
            elif self.state == 'active':
                await self.execute_task()
            await asyncio.sleep(random.uniform(0.1, 1.0))

    async def participate_in_consensus(self):
        self.state = 'consensus'
        print(f'Node {self.node_id} participating in consensus')
        
        # Reach consensus with neighbors
        await asyncio.gather(*[neighbor.propose_task() for neighbor in self.neighbors])
        
        # Elect leader and assign task
        leader = await self.elect_leader()
        if self.node_id == leader.node_id:
            self.task = self.generate_task()
            self.state = 'active'
            print(f'Node {self.node_id} elected as leader, executing task: {self.task}')
        else:
            self.state = 'idle'
            print(f'Node {self.node_id} not elected as leader')

    async def propose_task(self):
        # Simulate proposing a task to neighbors
        await asyncio.sleep(random.uniform(0.1, 1.0))
        return {'node_id': self.node_id, 'task': self.generate_task()}

    async def elect_leader(self) -> 'SwarmNode':
        # Simulate leader election algorithm
        proposals = await asyncio.gather(*[neighbor.propose_task() for neighbor in self.neighbors])
        leader_proposal = max(proposals, key=lambda p: p['task'])
        return next(filter(lambda n: n.node_id == leader_proposal['node_id'], self.neighbors))

    def generate_task(self) -> str:
        # Simulate generating a task
        return f'Task-{random.randint(1, 100)}'

    async def execute_task(self):
        print(f'Node {self.node_id} executing task: {self.task}')
        # Simulate executing the task
        await asyncio.sleep(random.uniform(1.0, 5.0))
        self.state = 'idle'
        print(f'Node {self.node_id} completed task: {self.task}')
