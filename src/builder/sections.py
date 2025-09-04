from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple, Union, cast

from .helpers import (
    _is_stage_class,
    _norm_key,
    _title_from_key,
    _try_import_generated_stages,
    _CriticalStep,
)
from .items import Item, PromptText, ItemLike, _as_item
from .preferences import IndentationPreferences


try:
    from dynamic_prompt.stage_contract import Stage  # type: ignore
except Exception:  # pragma: no cover
    class Stage:  # type: ignore
        pass


@dataclass
class PromptSection(Item):
    title: str
    items: List[Item] = field(default_factory=list)
    key: Optional[str] = None
    subtitle: Optional[str] = None
    bullet_style: str | None | bool = True
    _subindex: Dict[str, "PromptSection"] = field(default_factory=dict, init=False, repr=False)
    _critical_steps: List[_CriticalStep] = field(default_factory=list, init=False, repr=False)

    def __init__(
        self,
        name: Optional[Union[str, Enum, Stage, type]] = None,
        items: Optional[Sequence[ItemLike]] = None,
        *,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        bullet_style: str | None | bool = True,
    ):
        self.key = _norm_key(name) if name is not None else None
        self.title = title if title is not None else (_title_from_key(name) if name is not None else "")
        self.subtitle = subtitle
        self.bullet_style = bullet_style

        self.items = []
        self._subindex = {}
        self._critical_steps = []

        if items:
            for it in items:
                self.add_item(it)

    def _propagate_stage_root_to(self, child: "PromptSection") -> None:
        if hasattr(self, "_stage_root"):
            child._stage_root = getattr(self, "_stage_root", None)
            child._stage_root_name = getattr(self, "_stage_root_name", "")

    def add_item(self, item) -> "PromptSection | None":
        if isinstance(item, Item):
            self.items.append(item)
            if isinstance(item, PromptSection):
                if not item.key:
                    item.key = _norm_key(item.title)
                self._subindex.setdefault(item.key, item)
                self._propagate_stage_root_to(item)
            return None

        if isinstance(item, str):
            self.items.append(PromptText(item))
            return None

        if isinstance(item, tuple) and len(item) >= 1:
            name = item[0]
            key_norm = _norm_key(name)
            sec = self._subindex.get(key_norm)
            if sec is None:
                subtitle = item[2] if len(item) >= 3 else None
                sec = PromptSection(name, subtitle=subtitle)
                self._propagate_stage_root_to(sec)
                self.items.append(sec)
                self._subindex[key_norm] = sec
            if len(item) >= 2:
                payload = item[1]
                if isinstance(payload, (list, tuple)):
                    for x in payload:
                        sec.add_item(x)
                elif payload is not None:
                    sec.add_item(payload)
            return sec

        self.items.append(PromptText(str(item)))
        return None

    def add_critical_step(self, title: str, description: str) -> None:
        self._critical_steps.append(_CriticalStep(title=title.strip(), description=description.strip()))

    def __getitem__(self, key):
        k = _norm_key(key)
        sec = self._subindex.get(k)
        if sec is None:
            title = _title_from_key(key)
            sec = PromptSection(key, title=title)
            sec.key = k
            if _is_stage_class(key):
                setattr(sec, "_stage_cls", key)
            self.items.append(sec)
            self._subindex[k] = sec
        return sec

    def __setitem__(
        self,
        key: Union[str, Enum, Stage, type],
        value: Union[
            str,
            "PromptSection",
            Item,
            Sequence[ItemLike],
            Tuple[str, Sequence[ItemLike]],
            Tuple[str, Sequence[ItemLike], str],
        ],
    ) -> None:
        if _is_stage_class(key):
            cls = cast(type, key)
            path = self._path_from_stage_class(cls)
            if isinstance(value, PromptSection):
                self._set_section_by_path(path, value)
            else:
                self._assign_by_path(path, value)
            return

        k = _norm_key(key)

        if isinstance(value, PromptSection):
            k = _norm_key(key)
            value.key = k
            if not value.title or value.title.lower() == "none":
                value.title = _title_from_key(key)
            if hasattr(self, "_stage_root"):
                self._propagate_stage_root_to(value)

            self._subindex[k] = value
            for i, item in enumerate(self.items):
                if isinstance(item, PromptSection) and item.key == k:
                    if hasattr(item, "_insertion_seq") and not hasattr(value, "_insertion_seq"):
                        setattr(value, "_insertion_seq", getattr(item, "_insertion_seq"))
                    self.items[i] = value
                    break
            else:
                self.items.append(value)
            return

        if isinstance(value, str):
            if k in self._subindex:
                self._subindex[k].items.append(_as_item(value))
            else:
                new_sec = PromptSection(key, items=[_as_item(value)])
                if hasattr(self, "_stage_root"):
                    self._propagate_stage_root_to(new_sec)
                self.items.append(new_sec)
                self._subindex[k] = new_sec
            return

        if isinstance(value, tuple) and len(value) >= 2 and isinstance(value[0], str):
            sec_title = value[0]
            items = value[1]
            if not isinstance(items, (list, tuple)):
                raise TypeError("Second element of tuple must be a sequence of items")
            subtitle = value[2] if len(value) >= 3 else None
            items_list = [_as_item(v) for v in items]
            new_sec = PromptSection(key, items=items_list, title=sec_title, subtitle=subtitle)
            if hasattr(self, "_stage_root"):
                self._propagate_stage_root_to(new_sec)
        elif isinstance(value, (list, tuple)):
            items_list = [_as_item(v) for v in value]
            new_sec = PromptSection(key, items=items_list)
            if hasattr(self, "_stage_root"):
                self._propagate_stage_root_to(new_sec)
        else:
            raise TypeError(
                "__setitem__ expects str, PromptSection, a sequence, (title, sequence), or (title, sequence, subtitle)"
            )

        new_sec.key = k
        if k in self._subindex:
            existing = self._subindex[k]
            existing.items.extend(new_sec.items)
            if existing.subtitle is None and new_sec.subtitle:
                existing.subtitle = new_sec.subtitle
        else:
            self.items.append(new_sec)
            self._subindex[k] = new_sec

    def _assign_by_path(
        self,
        path: List[object],
        value: Union[
            str, Item, Sequence[ItemLike], Tuple[str, Sequence[ItemLike]], Tuple[str, Sequence[ItemLike], str]
        ],
    ) -> None:
        cur = self
        for name in path[:-1]:
            sec = cur[name]
            if not sec.title:
                sec.title = _title_from_key(name)
            if not sec.key:
                sec.key = _norm_key(name)
            cur = sec

        leaf_key_obj = path[-1] if path else "Section"
        leaf = cur[leaf_key_obj]
        if not leaf.title:
            leaf.title = _title_from_key(leaf_key_obj)
        if not leaf.key:
            leaf.key = _norm_key(leaf_key_obj)

        if path and hasattr(self, "_register_top_stage_from_class"):
            first = path[0]
            if _is_stage_class(first):
                top_sec = self[first]
                # type: ignore[attr-defined]
                self._register_top_stage_from_class(first, top_sec)

        self._append_into_section(leaf, value)

    def _path_from_stage_class(self, cls: type) -> List[str]:
        qual = getattr(cls, "__qualname__", "")
        parts = qual.split(".")
        if not parts:
            return []
        return parts[1:] if len(parts) > 1 else parts

    def _set_section_by_path(self, path: List[object], new_sec: "PromptSection") -> None:  # shared impl
        parent: PromptSection = self
        for name in path[:-1]:
            sec = parent[name]
            if not sec.title:
                sec.title = _title_from_key(name)
            if not sec.key:
                sec.key = _norm_key(name)
            parent = sec

        leaf_key_obj = path[-1] if path else "Section"
        leaf_key = _norm_key(leaf_key_obj)

        new_sec.key = leaf_key
        if not new_sec.title:
            new_sec.title = _title_from_key(leaf_key_obj)

        if hasattr(self, "_stage_root"):
            self._propagate_stage_root_to(new_sec)

        replaced = False
        for i, item in enumerate(parent.items):
            if isinstance(item, PromptSection) and item.key == leaf_key:
                if hasattr(item, "_insertion_seq") and not hasattr(new_sec, "_insertion_seq"):
                    setattr(new_sec, "_insertion_seq", getattr(item, "_insertion_seq"))
                parent.items[i] = new_sec
                replaced = True
                break

        parent._subindex[leaf_key] = new_sec
        if not replaced:
            parent.items.append(new_sec)

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
            heading_prefix = ""
            cur_style_for_children = prev_style
        else:
            cur_style = prefs.next_style(prev_style)
            heading_prefix = prefs.bullet_from_style(cur_style, idx)
            cur_style_for_children = cur_style

        left = " " * (prefs.spaces_per_level * level)
        hang = " " * (prefs.spaces_per_level * level + len(heading_prefix))
        heading = self.title
        lines = [left + heading_prefix + heading]

        for cs in self._critical_steps:
            desc_lines = cs.description.splitlines() or [""]
            lines.append(hang + f"!!! MANDATORY STEP [{cs.title}] !!!")
            for dl in desc_lines:
                lines.append(hang + dl.strip())
            lines.append(hang + "!!! END MANDATORY STEP !!!")

        if self.subtitle:
            lines.append(hang + self.subtitle)

        next_level = level + 1
        children_ignore = self.bullet_style is None

        for i, child in enumerate(self.items, 1):
            lines.append(
                child.render(
                    idx=i,
                    level=next_level,
                    prefs=prefs,
                    prev_style=cur_style_for_children,
                    ignore_bullets=children_ignore,
                )
            )

        return "\n".join(lines)

    def _append_into_section(
        self,
        section: "PromptSection",
        value: Union[
            str,
            Item,
            Sequence[ItemLike],
            Tuple[str, Sequence[ItemLike]],
            Tuple[str, Sequence[ItemLike], str],
        ],
    ) -> None:
        if isinstance(value, str):
            section.items.append(_as_item(value))
            return
        if isinstance(value, Item):
            section.items.append(value)
            return
        if isinstance(value, tuple) and len(value) >= 2 and isinstance(value[0], str):
            sec_title = value[0]
            items = value[1]
            if not isinstance(items, (list, tuple)):
                raise TypeError("Second element of tuple must be a sequence of items")
            subtitle = value[2] if len(value) >= 3 else None
            if sec_title:
                section.title = sec_title
            if subtitle and section.subtitle is None:
                section.subtitle = subtitle
            for it in items:
                section.items.append(_as_item(it))
            return
        for it in value:  # type: ignore[arg-type]
            section.items.append(_as_item(it))




