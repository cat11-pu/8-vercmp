# -*- coding: utf-8 -*-
"""验收：三类电池逐条比对（期望值取自真 packaging 的实测）。

用法：python3 check_vercmp.py
"""
import json
import sys

sys.path.insert(0, ".")
import vercmp  # noqa: E402

BATTERY = json.loads(r"""{
 "normalized": {
  "1.0": "1.0",
  "1.0.0": "1.0.0",
  "v1.0": "1.0",
  "1.0a": "1.0a0",
  "1.0a1": "1.0a1",
  "1.0.RC1": "1.0rc1",
  "1.0.alpha1": "1.0a1",
  "1.0post1": "1.0.post1",
  "1.0-1": "1.0.post1",
  "1.0.post1": "1.0.post1",
  "1.0.dev1": "1.0.dev1",
  "1.0+abc.1": "1.0+abc.1",
  "1.0 ": "1.0",
  " 1.0": "1.0",
  "1.0.0.0": "1.0.0.0",
  "0!1.0": "1.0",
  "1!1.0": "1!1.0",
  "1.0+ABC": "1.0+abc",
  "1.0+abc-1": "1.0+abc.1",
  "10.0": "10.0",
  "1.0rc1": "1.0rc1"
 },
 "cmp": {
  "1.0|1.0.0": 0,
  "1.0|1.0.1": -1,
  "1.0a1|1.0a2": -1,
  "1.0a2|1.0b1": -1,
  "1.0b1|1.0rc1": -1,
  "1.0rc1|1.0": -1,
  "1.0.dev1|1.0a1": -1,
  "1.0.dev1|1.0.dev2": -1,
  "1.0|1.0.post1": -1,
  "1.0.post1|1.0.post2": -1,
  "1.0|1.0+local": -1,
  "1.0+abc|1.0+abd": -1,
  "1.0+abc|1.0+abc.1": -1,
  "1!1.0|2.0": 1,
  "1.0|1!0.1": -1,
  "2.0|10.0": -1,
  "1.0post1|1.0.post1": 0,
  "1.0-1|1.0.post1": 0,
  "v1.0|1.0": 0,
  "1.0.RC1|1.0rc1": 0,
  "1.0.alpha1|1.0a1": 0,
  "0.9|1.0.dev1": -1
 },
 "bad": {
  "1.0..0": "非法",
  "1.0+": "非法",
  "": "非法",
  "1.0_2": "非法",
  "one.two": "非法",
  "1.0-": "非法",
  "+1.0": "非法",
  "1.0+abc+def": "非法"
 }
}""")


def main():
    bad = 0
    total = 0

    for text in sorted(BATTERY["normalized"]):
        want = BATTERY["normalized"][text]
        total += 1
        try:
            got = vercmp.normalize(text)
        except Exception as error:  # noqa: BLE001
            got = "抛错:" + str(error)[:30]
        if got == want:
            print("通过 normalize(%r) = %s" % (text, want))
        else:
            bad += 1
            print("不过 normalize(%r) 期望 %s 实际 %s" % (text, want, got))

    for pair in sorted(BATTERY["cmp"]):
        a, b = pair.split("|")
        want = BATTERY["cmp"][pair]
        total += 1
        try:
            got = vercmp.compare(a, b)
        except Exception as error:  # noqa: BLE001
            got = "抛错:" + str(error)[:30]
        if got == want:
            print("通过 compare(%r, %r) = %s" % (a, b, want))
        else:
            bad += 1
            print("不过 compare(%r, %r) 期望 %s 实际 %s" % (a, b, want, got))

    for text in sorted(BATTERY["bad"]):
        total += 1
        try:
            vercmp.normalize(text)
            bad += 1
            print("不过 非法版本没被拒绝：%r" % text)
        except ValueError:
            print("通过 非法版本被拒绝：%r" % text)
        except Exception as error:  # noqa: BLE001
            bad += 1
            print("不过 非法版本抛了别的异常：%r -> %s" % (text, error))

    print("通过率 %d/%d" % (total - bad, total))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
