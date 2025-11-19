from __future__ import annotations

import re
import re as _re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

# Optional runtime Stage dataclass fallback
try:
    from dynamic_prompt.stage_contract import Stage  # type: ignore
except Exception:  # pragma: no cover

    @dataclass
    class Stage:  # fallback minimal stub
        name: str
        _parent: Optional[Stage] = None
        _root: Optional[Stage] = None

        def path(self) -> List[Stage]:
            cur: Optional[Stage] = self
            out: List[Stage] = []
            while cur:
                out.append(cur)
                cur = cur._parent
            return list(reversed(out))


def _try_import_generated_stages():
    try:
        from hyper_reasoning.prompts import prompt_structure as _ps  # noqa: F401
    except Exception:
        return None, {}

    Stages = getattr(_ps, "Stages", None)
    top_map = getattr(_ps, "TOP_ORDER_MAP", None)

    if Stages is not None and not top_map:
        tm: Dict[str, Tuple[int, bool]] = {}
        for idx, (nm, obj) in enumerate(Stages.__dict__.items()):
            if isinstance(obj, type) and hasattr(obj, "__stage_display__"):
                fixed = bool(getattr(obj, "__order_fixed__", False))
                order_index = int(getattr(obj, "__order_index__", idx))
                class_key = nm.strip().lower()
                display = getattr(obj, "__stage_display__", nm)
                display_key = display.strip().lower()
                for k in set(_key_variants(class_key) + _key_variants(display_key)):
                    tm[k] = (order_index, fixed)
        top_map = tm
    return Stages, top_map or {}


@dataclass
class _CriticalStep:
    title: str
    description: str


def _key_variants(s: str) -> tuple[str, str, str]:
    s0 = (s or "").strip().lower()
    spaced = _re.sub(r"[\s_]+", " ", s0)
    compact = _re.sub(r"[\s_\-]+", "", s0)
    return (s0, spaced, compact)


def _is_stage_class(x: object) -> bool:
    return isinstance(x, type) and hasattr(x, "__stage_display__")


def _stage_class_display_and_key(cls: type) -> tuple[str, str]:
    display = getattr(cls, "__stage_display__", cls.__name__)
    key = cls.__name__.strip().lower()
    return display, key


def _norm_key(key: Union[str, Enum, object]) -> str:
    if _is_stage_class(key):
        _, k = _stage_class_display_and_key(key)
        return k
    if isinstance(key, type):
        return getattr(key, "__name__", "section").strip().lower()
    if _is_stage_class(key):
        return key.name.strip().lower()  # type: ignore[attr-defined]
    return str(key).strip().lower()


_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def _title_from_class_name(name: str) -> str:
    parts = _CAMEL_BOUNDARY.split(name)
    return " ".join(p.capitalize() for p in parts if p)


def _title_from_key(key):
    if _is_stage_class(key):
        display = getattr(key, "__stage_display__", key.__name__)
        display = display.strip()
        if not display:
            return ""
        if re.search(r"[_\s]", display):
            words = re.split(r"[_\s]+", display)
            return " ".join(w.capitalize() for w in words if w)
        return _title_from_class_name(display)

    if isinstance(key, Enum):
        raw = str(key.value).strip()
    else:
        raw = str(key).strip()

    if not raw:
        return ""
    if re.search(r"[_\s]", raw):
        words = re.split(r"[_\s]+", raw)
        return " ".join(w.capitalize() for w in words if w)
    return _title_from_class_name(raw)


def _letters(idx: int) -> str:
    s, n = [], idx
    while n > 0:
        n, r = divmod(n - 1, 26)
        s.append(chr(ord("a") + r))
    return "".join(reversed(s))
