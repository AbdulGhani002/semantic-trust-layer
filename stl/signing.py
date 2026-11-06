"""Signed records shared between the agents and the Coordinator."""
from __future__ import annotations

import base64
import json
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class Signer:
    def __init__(self, name: str, key_dir: Path):
        self.name = name
        path = key_dir / f"{name}.key"
        if path.exists():
            self.key = serialization.load_pem_private_key(path.read_bytes(), password=None)
        else:
            key_dir.mkdir(parents=True, exist_ok=True)
            self.key = Ed25519PrivateKey.generate()
            path.write_bytes(
                self.key.private_bytes(
                    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
                )
            )

    @property
    def public_key(self) -> bytes:
        return self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def sign(self, payload: dict) -> dict:
        signature = self.key.sign(canonical(payload))
        return {"signer": self.name, "payload": payload, "signature": base64.b64encode(signature).decode()}


class TrustRegistry:
    def __init__(self):
        self.keys: dict[str, Ed25519PublicKey] = {}

    def add(self, name: str, public_key: bytes) -> None:
        self.keys[name] = Ed25519PublicKey.from_public_bytes(public_key)

    def verify(self, envelope: dict) -> bool:
        key = self.keys.get(envelope.get("signer"))
        if key is None:
            return False
        try:
            key.verify(base64.b64decode(envelope["signature"]), canonical(envelope["payload"]))
        except (InvalidSignature, KeyError, ValueError):
            return False
        return True
