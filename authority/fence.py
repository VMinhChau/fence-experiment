from dataclasses import dataclass, field
from typing import Dict, Set, Tuple

AuthorityEpoch = Tuple[str, int]
SupportSet = Set[AuthorityEpoch]


@dataclass
class Artifact:
	artifact_id: str
	content: str
	support: SupportSet = field(default_factory=set)


class RevocationFrontier:
	"""Track the least valid epoch for each authority."""

	def __init__(self) -> None:
		self._frontier: Dict[str, int] = {}

	def get(self, authority: str) -> int:
		return self._frontier.get(authority, 0)

	def revoke(self, authority: str, new_epoch: int) -> None:
		current = self.get(authority)
		if new_epoch <= current:
			raise ValueError(
				f"New epoch {new_epoch} must be greater than "
				f"current frontier {current}."
			)
		self._frontier[authority] = new_epoch

	def is_live(self, support: SupportSet) -> bool:
		"""Return whether every support epoch meets its authority frontier."""
		for authority, epoch in support:
			if epoch < self.get(authority):
				return False
		return True


def propagate_support(*artifacts: Artifact) -> SupportSet:
	"""Return the union of the source artifacts' support sets."""
	support: SupportSet = set()
	for artifact in artifacts:
		support.update(artifact.support)
	return support


class Fence:
	"""Track semantic dependence and validate commits against revocations.

	This class does not grant or revoke authority.
	"""

	def __init__(self) -> None:
		self.frontier = RevocationFrontier()

	def derive(
		self,
		artifact_id: str,
		content: str,
		*sources: Artifact,
	) -> Artifact:
		support = propagate_support(*sources)
		return Artifact(
			artifact_id=artifact_id,
			content=content,
			support=support,
		)

	def validate_commit(self, artifact: Artifact) -> bool:
		return self.frontier.is_live(artifact.support)

	def revoke(self, authority: str, new_epoch: int) -> None:
		self.frontier.revoke(authority, new_epoch)