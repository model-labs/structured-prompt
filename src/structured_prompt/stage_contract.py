from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional


# ------------------------------------------------------------
# Optional Stage dataclass (kept for compatibility)
# ------------------------------------------------------------
@dataclass
class Stage:
    """
    Optional runtime stage object (name + hierarchy).
    You can still use Stage instances as keys; the infra will auto-build parents via path().
    """

    name: str
    parent: Optional["Stage"] = None
    children: Dict[str, "Stage"] = field(default_factory=dict)

    def add_child(self, child: "Stage") -> "Stage":
        child.parent = self
        self.children[child.name] = child
        return child

    def path(self) -> List["Stage"]:
        cur: Optional[Stage] = self
        out: List[Stage] = []
        while cur is not None:
            out.append(cur)
            cur = cur.parent
        out.reverse()
        return out

    def __str__(self) -> str:
        return self.name

    def __iter__(self) -> Iterator["Stage"]:
        return iter(self.children.values())
