"""JWE (encrypted JWT) helpers.

Uses jwcrypto with alg="dir" + enc="A256GCM": a single 32-byte symmetric key
(JWE_KEY env, base64-url encoded) is used directly as the AES-256-GCM key,
with no key-wrapping step. This is the simplest viable JWE setup and is
appropriate when the same service signs and verifies (no key distribution).

Token claims:
    {"sub": <user_id>, "exp": <unix-seconds>, "iat": <unix-seconds>}
"""
from __future__ import annotations

import base64
import json
import os
import time
from typing import Optional

from jwcrypto import jwe, jwk
from jwcrypto.common import JWException

COOKIE_NAME = "session"
_ALG = "dir"
_ENC = "A256GCM"

_key_cache: Optional[jwk.JWK] = None


def _load_key() -> jwk.JWK:
    """Decode JWE_KEY (base64-url, 32 bytes) once and reuse."""
    global _key_cache
    if _key_cache is not None:
        return _key_cache

    raw = os.getenv("JWE_KEY", "").strip()
    if not raw:
        raise RuntimeError(
            "JWE_KEY is not set. Generate one with: "
            "python -c \"import secrets, base64; "
            "print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())\""
        )

    # Accept urlsafe base64, with or without padding.
    padded = raw + "=" * (-len(raw) % 4)
    try:
        key_bytes = base64.urlsafe_b64decode(padded)
    except Exception as exc:
        raise RuntimeError("JWE_KEY is not valid base64-url") from exc

    if len(key_bytes) != 32:
        raise RuntimeError(
            f"JWE_KEY must decode to exactly 32 bytes (got {len(key_bytes)}). "
            "Regenerate with the snippet in backend/.env.example."
        )

    _key_cache = jwk.JWK(kty="oct", k=base64.urlsafe_b64encode(key_bytes).rstrip(b"=").decode())
    return _key_cache


def _ttl_seconds() -> int:
    minutes = int(os.getenv("JWE_TTL_MINUTES", "10080"))  # default 7 days
    return minutes * 60


def encode(user_id: str) -> str:
    """Return a JWE compact serialization carrying {sub, iat, exp}."""
    key = _load_key()
    now = int(time.time())
    claims = {
        "sub": user_id,
        "iat": now,
        "exp": now + _ttl_seconds(),
    }
    token = jwe.JWE(
        plaintext=json.dumps(claims).encode("utf-8"),
        protected={"alg": _ALG, "enc": _ENC, "typ": "JWT"},
    )
    token.add_recipient(key)
    return token.serialize(compact=True)


def decode(serialized: str) -> Optional[dict]:
    """Decrypt + validate. Returns claims dict on success, None on any failure."""
    if not serialized:
        return None
    key = _load_key()
    try:
        token = jwe.JWE()
        token.deserialize(serialized, key=key)
        claims = json.loads(token.payload.decode("utf-8"))
    except (JWException, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    exp = claims.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        return None
    if not claims.get("sub"):
        return None
    return claims
