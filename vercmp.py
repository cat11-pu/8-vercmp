# -*- coding: utf-8 -*-
"""版本号规范化与比较（PEP 440 子集）。规格见 spec.md。"""

import re

_PRE_MARK = r"alpha|beta|preview|pre|rc|a|b|c"

_VERSION_RE = re.compile(
    r"^"
    r"(?:(?P<epoch>[0-9]+)!)?"
    r"(?P<release>[0-9]+(?:\.[0-9]+)*)"
    r"(?:[-_.]?(?P<pre>(?:" + _PRE_MARK + r"))(?P<pre_n>[0-9]*))?"
    r"(?:"
    r"(?:[-_.]?(?P<post>post|rev|r)(?P<post_n>[0-9]*))"
    r"|-(?P<dash_post_n>[0-9]+)"
    r")?"
    r"(?:[-_.]?(?P<dev>dev)(?P<dev_n>[0-9]*))?"
    r"$",
    re.IGNORECASE,
)

_LOCAL_SEG_RE = re.compile(r"[0-9A-Za-z]+\Z")
_PRE_KIND = {"a": "a", "alpha": "a", "b": "b", "beta": "b",
             "c": "rc", "rc": "rc", "pre": "rc", "preview": "rc"}
_PRE_ORDER = {"a": 0, "b": 1, "rc": 2}


def _parse(text):
    if not isinstance(text, str):
        raise ValueError("版本必须是字符串: %r" % (text,))
    core = text.strip()
    if core[:1] in ("v", "V"):
        core = core[1:]

    local_segments = None
    if "+" in core:
        core, plus, local_part = core.partition("+")
        if not plus or not local_part or "+" in local_part:
            raise ValueError("非法版本: %r" % (text,))
        local_segments = re.split(r"[-_.]", local_part)
        if not local_segments or any(
                not _LOCAL_SEG_RE.match(seg) for seg in local_segments):
            raise ValueError("非法版本: %r" % (text,))

    match = _VERSION_RE.match(core)
    if match is None:
        raise ValueError("非法版本: %r" % (text,))

    epoch = int(match.group("epoch")) if match.group("epoch") else 0
    release = match.group("release")

    pre = None
    if match.group("pre") is not None:
        kind = _PRE_KIND[match.group("pre").lower()]
        pre = (kind, int(match.group("pre_n") or 0))

    post = None
    if match.group("post") is not None:
        post = int(match.group("post_n") or 0)
    elif match.group("dash_post_n") is not None:
        post = int(match.group("dash_post_n"))

    dev = None
    if match.group("dev") is not None:
        dev = int(match.group("dev_n") or 0)

    return {
        "epoch": epoch,
        "release": release,
        "release_nums": tuple(int(seg) for seg in release.split(".")),
        "pre": pre,
        "post": post,
        "dev": dev,
        "local": None if local_segments is None
        else [seg.lower() for seg in local_segments],
    }


def normalize(text):
    parts = _parse(text)
    out = ""
    if parts["epoch"] != 0:
        out += "%d!" % parts["epoch"]
    out += parts["release"]
    if parts["pre"] is not None:
        out += "%s%d" % parts["pre"]
    if parts["post"] is not None:
        out += ".post%d" % parts["post"]
    if parts["dev"] is not None:
        out += ".dev%d" % parts["dev"]
    if parts["local"] is not None:
        out += "+" + ".".join(parts["local"])
    return out


def _comparison_key(parts):
    pre, post, dev = parts["pre"], parts["post"], parts["dev"]
    if pre is None and post is None and dev is not None:
        pre_key = (-1, 0, 0)
    elif pre is None:
        pre_key = (1, 0, 0)
    else:
        pre_key = (0, _PRE_ORDER[pre[0]], pre[1])

    post_key = (0, 0) if post is None else (1, post)
    dev_key = (1, 0) if dev is None else (0, dev)

    if parts["local"] is None:
        local_key = (0, ())
    else:
        segments = tuple(
            (1, int(seg)) if seg.isdigit() else (0, seg)
            for seg in parts["local"]
        )
        local_key = (1, segments)

    return (pre_key, post_key, dev_key, local_key)


def compare(a, b):
    parts_a = _parse(a)
    parts_b = _parse(b)
    width = max(len(parts_a["release_nums"]), len(parts_b["release_nums"]))
    key_a = (parts_a["epoch"],
             parts_a["release_nums"] + (0,) * (width - len(parts_a["release_nums"])),
             _comparison_key(parts_a))
    key_b = (parts_b["epoch"],
             parts_b["release_nums"] + (0,) * (width - len(parts_b["release_nums"])),
             _comparison_key(parts_b))
    if key_a < key_b:
        return -1
    if key_a > key_b:
        return 1
    return 0
