import hashlib
import json
import time


class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


class VotingBlockchain:
    def __init__(self):
        self.chain = [self._create_genesis_block()]
        self.voter_ids = set()

    def _create_genesis_block(self):
        return Block(0, time.time(), {"message": "Genesis Block - Election Start"}, "0")

    def cast_vote(self, student_id, candidate):
        if student_id in self.voter_ids:
            return False, "This student ID has already voted."

        self.voter_ids.add(student_id)
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={"student_id": student_id, "candidate": candidate},
            previous_hash=previous_block.hash,
        )
        self.chain.append(new_block)
        return True, "Vote recorded successfully!"

    def get_results(self):
        results = {}
        for block in self.chain[1:]:
            candidate = block.data["candidate"]
            results[candidate] = results.get(candidate, 0) + 1
        return results

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_chain(self):
        return [block.to_dict() for block in self.chain]
