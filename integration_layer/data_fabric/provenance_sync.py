"""
Provenance Sync – cryptographic evidence chain for every artifact, decision,
and knowledge claim that moves through the KCN ecosystem.

Design goals
------------
1. Every significant object receives a ProvenanceRecord that is content-addressed and hash-linked.
2. Records form immutable chains so any later claim can be traced back to its originating evidence.
3. The layer never stores the payload itself – only hashes, metadata, and signatures.
4. Compatible with the evidence packages used by OS-32/33 and external evaluation campaigns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
import hashlib
import json
import uuid


class HashAlgorithm(str, Enum):
    SHA256 = "sha256"
    SHA3_256 = "sha3_256"
    BLAKE2B = "blake2b"


class ProvenanceRecord(BaseModel):
    record_id: str
    subject_id: str
    subject_type: str
    action: str
    actor_id: str
    parent_ids: List[str] = Field(default_factory=list)
    content_hash: str
    hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    signature: Optional[str] = None

    @staticmethod
    def compute_content_hash(
        payload: bytes | str | dict,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
    ) -> str:
        if isinstance(payload, dict):
            data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        elif isinstance(payload, str):
            data = payload.encode()
        else:
            data = payload

        if algorithm == HashAlgorithm.SHA256:
            return hashlib.sha256(data).hexdigest()
        if algorithm == HashAlgorithm.SHA3_256:
            return hashlib.sha3_256(data).hexdigest()
        if algorithm == HashAlgorithm.BLAKE2B:
            return hashlib.blake2b(data).hexdigest()
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    @classmethod
    def create(
        cls,
        subject_id: str,
        subject_type: str,
        action: str,
        actor_id: str,
        content: bytes | str | dict,
        parent_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        algorithm: HashAlgorithm = HashAlgorithm.SHA256,
        signature: Optional[str] = None,
    ) -> "ProvenanceRecord":
        content_hash = cls.compute_content_hash(content, algorithm)
        record_payload = {
            "subject_id": subject_id,
            "subject_type": subject_type,
            "action": action,
            "actor_id": actor_id,
            "parent_ids": sorted(parent_ids or []),
            "content_hash": content_hash,
            "hash_algorithm": algorithm.value,
            "metadata": metadata or {},
        }
        record_id = cls.compute_content_hash(record_payload, algorithm)

        return cls(
            record_id=record_id,
            subject_id=subject_id,
            subject_type=subject_type,
            action=action,
            actor_id=actor_id,
            parent_ids=parent_ids or [],
            content_hash=content_hash,
            hash_algorithm=algorithm,
            metadata=metadata or {},
            signature=signature,
        )


class ProvenanceChain(BaseModel):
    root_subject_id: str
    records: List[ProvenanceRecord]
    verified: bool = False
    verification_notes: List[str] = Field(default_factory=list)


class ProvenanceSync:
    def __init__(self) -> None:
        self._records: Dict[str, ProvenanceRecord] = {}
        self._children: Dict[str, Set[str]] = {}
        self._by_subject: Dict[str, List[str]] = {}

    def record(self, prov: ProvenanceRecord) -> ProvenanceRecord:
        if prov.record_id in self._records:
            return self._records[prov.record_id]
        self._records[prov.record_id] = prov
        self._by_subject.setdefault(prov.subject_id, []).append(prov.record_id)
        for parent_id in prov.parent_ids:
            self._children.setdefault(parent_id, set()).add(prov.record_id)
        return prov

    def get(self, record_id: str) -> Optional[ProvenanceRecord]:
        return self._records.get(record_id)

    def get_for_subject(self, subject_id: str) -> List[ProvenanceRecord]:
        ids = self._by_subject.get(subject_id, [])
        return [self._records[i] for i in ids if i in self._records]

    def children_of(self, record_id: str) -> List[ProvenanceRecord]:
        child_ids = self._children.get(record_id, set())
        return [self._records[i] for i in child_ids if i in self._records]

    def build_chain(self, subject_id: str, *, max_depth: int = 50) -> ProvenanceChain:
        visited: Set[str] = set()
        ordered: List[ProvenanceRecord] = []
        notes: List[str] = []
        frontier = list(self._by_subject.get(subject_id, []))
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: List[str] = []
            for rid in frontier:
                if rid in visited:
                    continue
                visited.add(rid)
                rec = self._records.get(rid)
                if rec is None:
                    notes.append(f"Missing record {rid}")
                    continue
                ordered.append(rec)
                next_frontier.extend(rec.parent_ids)
            frontier = next_frontier
            depth += 1
        if depth >= max_depth:
            notes.append(f"Truncated at max_depth={max_depth}")
        ordered.reverse()
        chain = ProvenanceChain(root_subject_id=subject_id, records=ordered, verification_notes=notes)
        chain.verified = self._verify_chain(chain)
        return chain

    def _verify_chain(self, chain: ProvenanceChain) -> bool:
        seen: Set[str] = set()
        for rec in chain.records:
            if rec.record_id in seen:
                chain.verification_notes.append(f"Cycle detected at {rec.record_id}")
                return False
            seen.add(rec.record_id)
            record_payload = {
                "subject_id": rec.subject_id,
                "subject_type": rec.subject_type,
                "action": rec.action,
                "actor_id": rec.actor_id,
                "parent_ids": sorted(rec.parent_ids),
                "content_hash": rec.content_hash,
                "hash_algorithm": rec.hash_algorithm.value,
                "metadata": rec.metadata,
            }
            expected_id = ProvenanceRecord.compute_content_hash(record_payload, rec.hash_algorithm)
            if rec.record_id != expected_id:
                chain.verification_notes.append(f"Record digest mismatch at {rec.record_id}")
                return False
            for pid in rec.parent_ids:
                if pid not in self._records:
                    chain.verification_notes.append(f"Dangling parent {pid}")
                    return False
        return len(chain.verification_notes) == 0

    def export_evidence_package(self, subject_id: str) -> Dict[str, Any]:
        chain = self.build_chain(subject_id)
        return {
            "subject_id": subject_id,
            "verified": chain.verified,
            "record_count": len(chain.records),
            "records": [r.model_dump(mode="json") for r in chain.records],
            "verification_notes": chain.verification_notes,
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }
