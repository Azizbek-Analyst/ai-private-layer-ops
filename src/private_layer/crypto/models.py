"""Bundle and crypto-related data structures."""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from private_layer.crypto.errors import BundleValidationError


@dataclass(frozen=False)
class Bundle:
    """
    Encrypted fragment bundle. Must contain exactly:
    id, nonce_b64, cipher_b64, aad, wrapped_dek, key_version; optional salt.
    """

    id: str  # token_id
    nonce_b64: str
    cipher_b64: str
    aad: str
    wrapped_dek: str
    key_version: str
    salt: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "id": self.id,
            "nonce_b64": self.nonce_b64,
            "cipher_b64": self.cipher_b64,
            "aad": self.aad,
            "wrapped_dek": self.wrapped_dek,
            "key_version": self.key_version,
        }
        if self.salt is not None:
            d["salt"] = self.salt
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Bundle":
        id_ = d.get("id")
        if id_ is None or id_ == "":
            raise BundleValidationError("Bundle missing required field: id")
        nonce_b64 = d.get("nonce_b64") or d.get("n")
        cipher_b64 = d.get("cipher_b64") or d.get("c")
        wrapped_dek = d.get("wrapped_dek") or d.get("wd")
        key_version = d.get("key_version") or d.get("kv")
        if not nonce_b64 or not cipher_b64 or not wrapped_dek or not key_version:
            raise BundleValidationError(
                "Bundle missing required field: need nonce_b64 (or n), cipher_b64 (or c), "
                "wrapped_dek (or wd), key_version (or kv)"
            )
        return cls(
            id=str(id_),
            nonce_b64=str(nonce_b64),
            cipher_b64=str(cipher_b64),
            aad=str(d["aad"]),
            wrapped_dek=str(wrapped_dek),
            key_version=str(key_version),
            salt=d.get("salt"),
        )
