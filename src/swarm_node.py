# Decentralized Swarm Node with Byzantine Fault Tolerance

import asyncio
import hashlib
from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Message:
    sender_id: str
    content: str
    timestamp: float
    signature: str

class SwarmNode:
    def __init__(self, node_id: str, private_key: str):
        self.node_id = node_id
        self.private_key = private_key
        self.peers: Set[str] = set()
        self.message_pool: List[Message] = []
        self.consensus_cache: Dict[str, int] = {}
        self.min_consensus = 2/3  # Byzantine fault tolerance threshold
        
    async def broadcast_message(self, content: str) -> None:
        """Broadcast a message to all peers in the swarm"""
        message = self._create_message(content)
        self.message_pool.append(message)
        
        for peer_id in self.peers:
            await self._send_to_peer(peer_id, message)
    
    def _create_message(self, content: str) -> Message:
        """Create a signed message"""
        timestamp = datetime.now().timestamp()
        msg_hash = hashlib.sha256(
            f"{self.node_id}{content}{timestamp}".encode()
        ).hexdigest()
        signature = self._sign_message(msg_hash)
        
        return Message(
            sender_id=self.node_id,
            content=content,
            timestamp=timestamp,
            signature=signature
        )
    
    async def receive_message(self, message: Message) -> bool:
        """Process received message and participate in consensus"""
        if not self._verify_message(message):
            return False
            
        self.message_pool.append(message)
        msg_hash = self._get_message_hash(message)
        
        # Update consensus count
        self.consensus_cache[msg_hash] = \
            self.consensus_cache.get(msg_hash, 0) + 1
            
        # Check if consensus threshold reached
        if self._check_consensus(msg_hash):
            await self._handle_consensus(message)
            return True
            
        return False
    
    def _check_consensus(self, msg_hash: str) -> bool:
        """Check if message has reached consensus threshold"""
        if msg_hash not in self.consensus_cache:
            return False
            
        consensus_count = self.consensus_cache[msg_hash]
        return consensus_count >= len(self.peers) * self.min_consensus
    
    async def _handle_consensus(self, message: Message) -> None:
        """Handle message that reached consensus"""
        # Implementation specific consensus handling
        print(f"Consensus reached for message: {message.content}")
    
    def _sign_message(self, msg_hash: str) -> str:
        """Sign message hash with node's private key"""
        # Simplified signing - replace with proper crypto
        return hashlib.sha256(
            f"{msg_hash}{self.private_key}".encode()
        ).hexdigest()
    
    def _verify_message(self, message: Message) -> bool:
        """Verify message signature and sender"""
        # Simplified verification - replace with proper crypto
        msg_hash = self._get_message_hash(message)
        expected_sig = hashlib.sha256(
            f"{msg_hash}{self.private_key}".encode()
        ).hexdigest()
        return message.signature == expected_sig
    
    def _get_message_hash(self, message: Message) -> str:
        """Get deterministic hash of message content"""
        return hashlib.sha256(
            f"{message.sender_id}{message.content}{message.timestamp}"
            .encode()
        ).hexdigest()
    
    async def _send_to_peer(self, peer_id: str, message: Message) -> None:
        """Send message to a specific peer"""
        # Implementation specific network transport
        pass

    def add_peer(self, peer_id: str) -> None:
        """Add new peer to the swarm"""
        self.peers.add(peer_id)

    def remove_peer(self, peer_id: str) -> None:
        """Remove peer from the swarm"""
        self.peers.discard(peer_id)