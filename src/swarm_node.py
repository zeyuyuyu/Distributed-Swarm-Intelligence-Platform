import asyncio
import random
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class NodeStatus:
    load: float  # Current CPU load (0-1)
    tasks_running: int
    last_heartbeat: float
    is_healthy: bool

class SwarmNode:
    def __init__(self, node_id: str, capacity: int = 100):
        self.node_id = node_id
        self.capacity = capacity
        self.tasks: Dict[str, asyncio.Task] = {}
        self.status = NodeStatus(
            load=0.0,
            tasks_running=0,
            last_heartbeat=0.0,
            is_healthy=True
        )
        self.peers: Dict[str, 'SwarmNode'] = {}
        self._heartbeat_interval = 5.0

    async def start(self):
        """Initialize the node and start background tasks"""
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._health_check_task = asyncio.create_task(self._health_check_loop())

    async def stop(self):
        """Gracefully shutdown the node"""
        self._heartbeat_task.cancel()
        self._health_check_task.cancel()
        await self._redistribute_tasks()

    async def add_task(self, task_id: str, coroutine) -> bool:
        """Add a new task to this node with load balancing"""
        if self.status.load >= 0.8:  # Load too high
            target_node = self._find_least_loaded_peer()
            if target_node:
                return await target_node.add_task(task_id, coroutine)
            
        if task_id in self.tasks:
            return False

        self.tasks[task_id] = asyncio.create_task(coroutine)
        self.status.tasks_running += 1
        self._update_load()
        return True

    async def remove_task(self, task_id: str) -> bool:
        """Remove and cancel a task"""
        if task_id not in self.tasks:
            return False

        task = self.tasks.pop(task_id)
        task.cancel()
        self.status.tasks_running -= 1
        self._update_load()
        return True

    def add_peer(self, node_id: str, node: 'SwarmNode'):
        """Add a peer node to the network"""
        self.peers[node_id] = node

    def remove_peer(self, node_id: str):
        """Remove a peer node from the network"""
        self.peers.pop(node_id, None)

    async def _heartbeat_loop(self):
        """Continuously send heartbeats to peers"""
        while True:
            self.status.last_heartbeat = asyncio.get_event_loop().time()
            await asyncio.sleep(self._heartbeat_interval)

    async def _health_check_loop(self):
        """Monitor health of peers and redistribute tasks if needed"""
        while True:
            current_time = asyncio.get_event_loop().time()
            for peer_id, peer in list(self.peers.items()):
                if current_time - peer.status.last_heartbeat > self._heartbeat_interval * 3:
                    peer.status.is_healthy = False
                    await self._handle_peer_failure(peer_id)
            await asyncio.sleep(self._heartbeat_interval)

    def _update_load(self):
        """Update the current load factor"""
        self.status.load = self.status.tasks_running / self.capacity

    def _find_least_loaded_peer(self) -> Optional['SwarmNode']:
        """Find the peer with the lowest load"""
        healthy_peers = [p for p in self.peers.values() if p.status.is_healthy]
        if not healthy_peers:
            return None
        return min(healthy_peers, key=lambda x: x.status.load)

    async def _handle_peer_failure(self, failed_peer_id: str):
        """Handle failure of a peer node"""
        failed_peer = self.peers[failed_peer_id]
        self.remove_peer(failed_peer_id)

        # Redistribute tasks from failed node
        tasks_to_redistribute = list(failed_peer.tasks.items())
        random.shuffle(tasks_to_redistribute)  # Randomize to avoid all tasks going to same node
        
        for task_id, task in tasks_to_redistribute:
            target_node = self._find_least_loaded_peer()
            if target_node:
                await target_node.add_task(task_id, task._coro)

    async def _redistribute_tasks(self):
        """Redistribute all tasks to peers before shutdown"""
        tasks = list(self.tasks.items())
        for task_id, task in tasks:
            await self.remove_task(task_id)
            target_node = self._find_least_loaded_peer()
            if target_node:
                await target_node.add_task(task_id, task._coro)
