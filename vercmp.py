# -*- coding: utf-8 -*-
"""PEP 440 子集：版本号规范化与比较。规格见 spec.md。"""

import re

# 骨架：[epoch!]release[pre][post][dev][+local]
# 预发布标记按长到短排列，避免 alpha 被开头的 a 抢走。
_VERSION_RE = re.compile(
    r"(?:(?P<epoch>[0-9]+)!)?"
    r"(?P<release>[0-9]+(?:\.[0-9]+)*)"
    r"(?:[-_.]?(?P<pre_l>alpha|beta|preview|pre|rc|c|b|a)"
    r"[-_.]?(?P<pre_n>[0-9]+)?)?"
    r"(?:-(?P<post_n1>[0-9]+)"
    r"|[-_.]?(?P<post_l>post|rev|r)[-_.]?(?P<post_n2>[0-9]+)?)?"
    r"(?:[-_.]?(?P<dev_l>dev)[-_.]?(?P<dev_n>[0-9]+)?)?"
    r"(?:\+(?P<local>[0-9a-z]+(?:[-_.][0-9a-z]+)*))?",
    re.IGNORECASE,
)

_PRE_MAP = {
    "a": "a",
    "alpha": "a",
    "b": "b",
    "beta": "b",
    "c": "rc",
    "rc": "rc",
    "pre": "rc",
    "preview": "rc",
}

_PRE_ORDER = {"a": 0, "b": 1, "rc": 2}


def _parse(text):
    """把合法版本解析成各部分；非法抛 ValueError。"""
    if not isinstance(text, str):
        raise ValueError("不是合法版本: %r" % (text,))
    s = text.strip()
    if s[:1] in ("v", "V"):
        s = s[1:]
    match = _VERSION_RE.fullmatch(s)
    if match is None:
        raise ValueError("不是合法版本: %r" % (text,))

    epoch = int(match.group("epoch") or 0)
    release = match.group("release").split(".")

    pre = None
    if match.group("pre_l") is not None:
        pre = (
            _PRE_MAP[match.group("pre_l").lower()],
            int(match.group("pre_n") or 0),
        )

    post = None
    if match.group("post_n1") is not None:
        post = int(match.group("post_n1"))
    elif match.group("post_l") is not None:
        post = int(match.group("post_n2") or 0)

    dev = None
    if match.group("dev_l") is not None:
        dev = int(match.group("dev_n") or 0)

    local = None
    if match.group("local") is not None:
        local = re.split(r"[-_.]", match.group("local").lower())

    return {
        "epoch": epoch,
        "release": release,
        "pre": pre,
        "post": post,
        "dev": dev,
        "local": local,
    }


def _cmp(x, y):
    return (x > y) - (x < y)


def _pre_key(parts):
    pre, post, dev = parts["pre"], parts["post"], parts["dev"]
    if pre is not None:
        return (0, _PRE_ORDER[pre[0]], pre[1])
    # 只有 dev 没有 pre（也没有 post）的版本比任何带预发布的都小。
    if post is None and dev is not None:
        return (-1,)
    # 没有预发布的正式版本比任何带预发布的都大。
    return (1,)


def _local_key(parts):
    if parts["local"] is None:
        return (-1, ())
    labels = []
    for segment in parts["local"]:
        if segment.isdigit():
            labels.append((1, int(segment), ""))  # 数字段比字母段大
        else:
            labels.append((0, 0, segment))
    return (0, tuple(labels))


def normalize(text):
    parts = _parse(text)
    result = ""
    if parts["epoch"] != 0:
        result += "%d!" % parts["epoch"]
    result += ".".join(parts["release"])
    if parts["pre"] is not None:
        result += "%s%d" % parts["pre"]
    if parts["post"] is not None:
        result += ".post%d" % parts["post"]
    if parts["dev"] is not None:
        result += ".dev%d" % parts["dev"]
    if parts["local"] is not None:
        result += "+" + ".".join(parts["local"])
    return result


def compare(a, b):
    left, right = _parse(a), _parse(b)

    result = _cmp(left["epoch"], right["epoch"])
    if result:
        return result

    left_release = [int(segment) for segment in left["release"]]
    right_release = [int(segment) for segment in right["release"]]
    length = max(len(left_release), len(right_release))
    left_release += [0] * (length - len(left_release))
    right_release += [0] * (length - len(right_release))
    result = _cmp(tuple(left_release), tuple(right_release))
    if result:
        return result

    result = _cmp(_pre_key(left), _pre_key(right))
    if result:
        return result

    left_post = (-1,) if left["post"] is None else (0, left["post"])
    right_post = (-1,) if right["post"] is None else (0, right["post"])
    result = _cmp(left_post, right_post)
    if result:
        return result

    # 有 dev 的比没有的小。
    left_dev = (1,) if left["dev"] is None else (0, left["dev"])
    right_dev = (1,) if right["dev"] is None else (0, right["dev"])
    result = _cmp(left_dev, right_dev)
    if result:
        return result

    return _cmp(_local_key(left), _local_key(right))
