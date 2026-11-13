#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步可莉「广告平台拦截器」（BlockAdvertisers）的 Surge 转换版，并做两处确定性修正。

数据源：kelee.one 屏蔽机房 IP（含 GitHub Actions），原站取不到；改取 Repcz/Tool 仓库
维护的 Kelee Surge 转换版（#!URL 指向原插件 BlockAdvertisers.lpx）。

修正（与手工版一致，幂等）：
  1. URL Rewrite 的分隔符残留 " _ reject" -> " - reject"（下划线不是 Surge 的合法写法）。
  2. AND 逻辑规则括号内 ", " -> ","（贴合 Surge 手册逻辑规则格式）。
  并在 #!date 后补一行修正说明注释（已存在则不重复加）。
安全：抓取失败或规则数 < 300 时非零退出，不改输出文件。
"""
import re
import sys
import urllib.request

SRC_URL = "https://raw.githubusercontent.com/Repcz/Tool/master/Surge/Module/Kelee/BlockAdvertisers.sgmodule"
OUT = "BlockAdvertisers.sgmodule"
NOTE = '# 本地修正：4 条 URL Rewrite 的分隔符由转换残留的 " _ reject" 改为 " - reject"；4 条 AND 规则括号内空格已去除（贴合 Surge 手册逻辑规则格式）。其余与 Repcz/Tool 的 Kelee 转换版一致。'


def main():
    try:
        req = urllib.request.Request(SRC_URL, headers={"User-Agent": "blockadv-sync"})
        with urllib.request.urlopen(req, timeout=60) as r:
            src = r.read().decode("utf-8")
    except Exception as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1

    out = []
    for line in src.splitlines():
        if " _ reject" in line:
            line = line.replace(" _ reject", " - reject")
        if line.startswith("AND,(("):
            line = re.sub(r",\s+", ",", line)
        out.append(line)
        if line.startswith("#!date=") and NOTE not in out:
            out.append(NOTE)
    text = "\n".join(out) + "\n"

    rules = [l for l in text.splitlines() if l.strip() and not l.startswith("#") and not l.startswith("[") and ("REJECT" in l or "DIRECT" in l)]
    if len(rules) < 300:
        print(f"rule count too low: {len(rules)}", file=sys.stderr)
        return 1

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"OK rules~{len(rules)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
