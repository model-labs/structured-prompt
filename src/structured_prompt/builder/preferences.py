from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class IndentationPreferences:
    spaces_per_level: int = 2
    progression: Tuple[str, ...] = ("number", "dash", "star", "loweralpha")
    fallback: str = "dash"
    blank_line_between_top: bool = True

    def style_for_level(self, level: int) -> str:
        return self.progression[level] if level < len(self.progression) else self.fallback

    def bullet_from_style(self, style: Optional[str], idx: int) -> str:
        if style is None:
            return ""
        if style == "number":
            return f"{idx}. "
        if style == "dash":
            return "- "
        if style == "star":
            return "* "
        if style == "loweralpha":
            n = idx
            out = []
            while n > 0:
                n, r = divmod(n - 1, 26)
                out.append(chr(ord("a") + r))
            return "".join(reversed(out)) + ". "
        return style if style.endswith(" ") else style + " "

    def bullet(self, level: int, idx: int) -> str:
        return self.bullet_from_style(self.style_for_level(level), idx)

    def next_style(self, prev_style: Optional[str]) -> str:
        if prev_style is None:
            return self.progression[0]
        try:
            i = self.progression.index(prev_style)
            j = i + 1
            if j < len(self.progression):
                return self.progression[j]
            return self.fallback
        except ValueError:
            return self.progression[0]


