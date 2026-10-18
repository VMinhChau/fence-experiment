"""
Conventional authority management baseline.

This module models an abstract authorization authority T.

The authority may represent, for example:

- a capability,
- a token-backed authorization,
- an approved authorization decision,
- or another trusted authorization grant.

IMPORTANT:

This module is NOT the FENCE mechanism.

It only models the control-plane fact that an agent has
authority T at a particular epoch.

FENCE separately tracks whether artifacts are semantically
derived from that authority.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class Authority:
    """
    One abstract authorization authority.

    In the FENCE model, this authority can be referred to as:

        T

    together with an authorization epoch:

        (T, epoch)
    """

    authority_id: str
    agent_id: str
    resource: str
    action: str
    epoch: int = 0
    status: str = "ACTIVE"


class AuthorityManager:
    """
    Conventional authorization control plane.

    This manager answers:

        "Does agent A currently have authority T
         to perform action X on resource R?"

    It does NOT track semantic derivation.

    That responsibility belongs to FENCE.
    """

    def __init__(self) -> None:
        self._authorities: Dict[
            Tuple[str, str, str],
            Authority,
        ] = {}

        self._next_epoch: Dict[str, int] = {}

    # ========================================================
    # Grant
    # ========================================================

    def grant(
        self,
        authority_id: str,
        agent_id: str,
        resource: str,
        action: str,
    ) -> Authority:

        epoch = self._next_epoch.get(authority_id, 0)

        authority = Authority(
            authority_id=authority_id,
            agent_id=agent_id,
            resource=resource,
            action=action,
            epoch=epoch,
            status="ACTIVE",
        )

        key = (
            agent_id,
            resource,
            action,
        )

        self._authorities[key] = authority

        return authority

    # ========================================================
    # Check
    # ========================================================

    def check(
        self,
        agent_id: str,
        resource: str,
        action: str,
    ) -> bool:

        key = (
            agent_id,
            resource,
            action,
        )

        authority = self._authorities.get(key)

        if authority is None:
            return False

        return authority.status == "ACTIVE"

    # ========================================================
    # Get active authority
    # ========================================================

    def get_authority(
        self,
        agent_id: str,
        resource: str,
        action: str,
    ) -> Authority | None:

        key = (
            agent_id,
            resource,
            action,
        )

        return self._authorities.get(key)

    # ========================================================
    # Revoke
    # ========================================================

    def revoke(
        self,
        agent_id: str,
        resource: str,
        action: str,
    ) -> Authority | None:

        key = (
            agent_id,
            resource,
            action,
        )

        authority = self._authorities.get(key)

        if authority is None:
            return None

        authority.status = "REVOKED"

        next_epoch = authority.epoch + 1
        self._next_epoch[authority.authority_id] = next_epoch

        return authority

    # ========================================================
    # Current epoch
    # ========================================================

    def current_epoch(
        self,
        authority_id: str,
    ) -> int:

        return self._next_epoch.get(
            authority_id,
            0,
        )