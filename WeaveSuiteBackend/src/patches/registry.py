import copy
from typing import Any, Dict

from .constants import DELETE

from . import sockshop, kubepay, lakeside

# Merge per-app registries. If two apps ever share a title (unlikely), the
# later import wins; if you want strictness, raise on collision.
ALL_PATCHES: Dict[str, Dict[str, Any]] = {
    **getattr(sockshop, "PATCHES_BY_TITLE_SUBSTR", {}),
    **getattr(kubepay, "PATCHES_BY_TITLE_SUBSTR", {}),
    **getattr(lakeside, "PATCHES_BY_TITLE_SUBSTR", {}),
}


def _parse_path(path: str) -> list:
    parts: list = []
    for seg in path.split("."):
        if "[" in seg:
            name, idx = seg.split("[", 1)
            if name:
                parts.append(name)
            parts.append(int(idx.rstrip("]")))
        else:
            parts.append(seg)
    return parts

def _set_at_path(node: dict, path: str, value: Any) -> None:
    keys = _parse_path(path)
    for k in keys[:-1]:
        if isinstance(k, int):
            node = node[k]
        else:
            nxt = node.get(k)
            if not isinstance(nxt, (dict, list)):
                return
            node = nxt
    last = keys[-1]
    if value is DELETE:
        if isinstance(node, dict):
            node.pop(last, None)
    else:
        node[last] = value


def apply_patches(spec: dict, patches: Dict[str, Any]) -> dict:
    out = copy.deepcopy(spec)
    for path, value in patches.items():
        _set_at_path(out, path, value)
    return out


def patched_spec(spec: dict) -> dict:
    title = spec.get("info", {}).get("title", "")
    for substr, patches in ALL_PATCHES.items():
        if substr in title:
            return apply_patches(spec, patches)
    return spec