# vercmp

仓库里是一份规格（`spec.md`，PEP 440 的子集：版本号的规范化与比较）、一个什么都没实现的桩
（`vercmp.py`）和一台验收（`check_vercmp.py`）。

## 你要做的

按 `spec.md` 把 `vercmp.py` 里的 `normalize(text)` 与 `compare(a, b)` 从零实现出来。
规格里的每一条都是硬约束：写法、规范化输出、比较顺序、非法版本的判定。

## 跑验收

    python3 check_vercmp.py

三类电池：规范化 21 条、比较 22 对、非法 8 条（这些期望值取自真实实现 pypa/packaging 的实测），
全部通过才退出码 0。

## 约束

- 只改 `vercmp.py`，不要动 `spec.md` 与 `check_vercmp.py`。
- 只用 Python 标准库（`re` 够用），不要引入依赖，也不要 import 任何第三方版本库。
