from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .helpers import _is_stage_class, _key_variants, _try_import_generated_stages
from .items import Item
from .preferences import IndentationPreferences
from .sections import PromptSection


@dataclass
class StructuredPromptFactory(PromptSection):
    prefs: IndentationPreferences = field(default_factory=IndentationPreferences)
    prologue: str | None = None
    stage_root: Optional[type] = None

    _top_order_map: Dict[str, Tuple[int, bool]] = field(init=False, default_factory=dict)
    _insertion_seq_counter: int = field(init=False, default=0)

    def __init__(
        self,
        prefs: IndentationPreferences | None = None,
        prologue: str | None = None,
        items: Sequence[Union[Item, str]] | None = None,
        title: str = "ROOT",
    ):
        super().__init__(name=title, items=items, title=title)
        self.prefs = prefs or IndentationPreferences()
        self.prologue = prologue

        self._top_order_map = {}
        Stages, topo = _try_import_generated_stages()
        self._stage_root = Stages
        self._stage_root_name = getattr(Stages, "__name__", "") if Stages else ""

        self._top_order_map.update(topo)
        self._insertion_seq_counter = 0

    def _register_top_stage_from_class(self, cls: type, section: "PromptSection") -> None:
        if not _is_stage_class(cls):
            return

        fixed = bool(getattr(cls, "__order_fixed__", False))
        order_index = int(getattr(cls, "__order_index__", 0))

        class_key = cls.__name__.strip().lower()
        display = getattr(cls, "__stage_display__", cls.__name__)
        display_key = str(display).strip().lower()

        for k in set(_key_variants(class_key) + _key_variants(display_key)):
            self._top_order_map[k] = (order_index, fixed)

        self._ensure_top_section_registered(section)

    def _ensure_top_section_registered(self, sec: PromptSection) -> None:
        if not hasattr(sec, "_insertion_seq"):
            setattr(sec, "_insertion_seq", self._insertion_seq_counter)
            self._insertion_seq_counter += 1

    def _top_fixed_index(self, sec: PromptSection) -> Optional[int]:
        if not self._top_order_map:
            return None

        candidates: List[str] = []
        if sec.key:
            candidates.extend(_key_variants(sec.key))
        if sec.title:
            candidates.extend(_key_variants(sec.title))

        for cand in candidates:
            hit = self._top_order_map.get(cand)
            if hit:
                order_index, is_fixed = hit
                if is_fixed:
                    return int(order_index)
        return None

    def _order_top_sections(self, top_sections: List[PromptSection]) -> List[PromptSection]:
        if not top_sections:
            return []

        for sec in top_sections:
            self._ensure_top_section_registered(sec)

        fixed_pairs: List[Tuple[int, PromptSection]] = []
        nonfixed: List[PromptSection] = []

        for sec in top_sections:
            fi = self._top_fixed_index(sec)
            if fi is not None:
                fixed_pairs.append((fi, sec))
            else:
                nonfixed.append(sec)

        if not fixed_pairs:
            return sorted(nonfixed, key=lambda s: getattr(s, "_insertion_seq", 1_000_000))

        max_idx = max(i for i, _ in fixed_pairs)
        slots: List[Optional[PromptSection]] = [None] * (max_idx + 1)

        seen_ids = set()
        overflow_nonfixed: List[PromptSection] = []
        for i, sec in sorted(fixed_pairs, key=lambda p: p[0]):
            if id(sec) in seen_ids:
                continue
            seen_ids.add(id(sec))
            if slots[i] is None:
                slots[i] = sec
            else:
                overflow_nonfixed.append(sec)

        nonfixed_all = nonfixed + overflow_nonfixed
        nonfixed_all.sort(key=lambda s: getattr(s, "_insertion_seq", 1_000_000))

        nf_idx = 0
        for pos in range(len(slots)):
            if slots[pos] is None and nf_idx < len(nonfixed_all):
                slots[pos] = nonfixed_all[nf_idx]
                nf_idx += 1

        ordered: List[PromptSection] = [s for s in slots if s is not None]

        if nf_idx < len(nonfixed_all):
            ordered.extend(nonfixed_all[nf_idx:])

        return ordered

    def render_prompt(self) -> str:
        parts: List[str] = []
        if self.prologue:
            parts.append(self.prologue.strip())
            parts.append("")

        if getattr(self, "_critical_steps", None):
            for cs in self._critical_steps:
                desc_lines = cs.description.splitlines() or [""]
                parts.append(f"!!! MANDATORY STEP [{cs.title}] !!!")
                for dl in desc_lines:
                    parts.append(dl.strip())
                parts.append("!!! END MANDATORY STEP !!!")
            parts.append("")

        top_sections: List[PromptSection] = [sec for sec in self.items if isinstance(sec, PromptSection)]

        for sec in top_sections:
            self._ensure_top_section_registered(sec)

        top_sorted: List[PromptSection] = self._order_top_sections(top_sections)

        for idx, child in enumerate(top_sorted, start=1):
            parts.append(child.render(idx=idx, level=0, prefs=self.prefs, prev_style=None, ignore_bullets=False))
            if self.prefs.blank_line_between_top:
                parts.append("")

        return "\n".join(parts).rstrip()
