from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple, Union

from .preferences import IndentationPreferences


class Item:
    def render(
        self,
        *,
        idx: int,
        level: int,
        prefs: IndentationPreferences,
        prev_style: Optional[str],
        ignore_bullets: bool,
    ) -> str:
        raise NotImplementedError


@dataclass
class PromptText(Item):
    text: str

    def render(
        self,
        *,
        idx: int,
        level: int,
        prefs: IndentationPreferences,
        prev_style: Optional[str],
        ignore_bullets: bool,
    ) -> str:
        if ignore_bullets:
            left = " " * (prefs.spaces_per_level * level)
            lines = self.text.strip().splitlines() or [""]
            out = [left + lines[0]]
            out += [left + ln.strip() for ln in lines[1:]]
            return "\n".join(out)

        cur_style = prefs.next_style(prev_style)
        prefix = prefs.bullet_from_style(cur_style, idx)
        left = " " * (prefs.spaces_per_level * level)
        hang = " " * (prefs.spaces_per_level * level + len(prefix))
        lines = self.text.strip().splitlines() or [""]
        out = [left + prefix + lines[0]]
        out += [hang + ln.strip() for ln in lines[1:]]
        return "\n".join(out)


ItemLike = Union[Item, str]


def _as_item(x: ItemLike) -> Item:
    return x if isinstance(x, Item) else PromptText(str(x))


