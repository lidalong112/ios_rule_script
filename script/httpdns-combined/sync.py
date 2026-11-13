#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将「可莉 HTTPDNS拦截器」与「blackmatrix7 BlockHTTPDNS」合并为一个 Surge 模块。

数据源：
  - 可莉版：kelee.one 屏蔽机房 IP（含 GitHub Actions），改从 GitHub 镜像 gys619/surge-tools
    的 Script Hub 转换版获取（与原插件 2026-07-04 版一致）。
  - blackmatrix7 版：直接取上游仓库 master 的 Surge 原生模块。

合并规则（确定性）：
  1. [General] 只取 blackmatrix7 的 force-http-engine-hosts（引擎层拦截，可莉版没有）。
  2. [Rule] 可莉的两条 AND DIRECT 例外（嘀嗒出行）置顶——它们必须先于通用拦截正则命中；
     其后是可莉全部规则（原文顺序，精确去重），再追加 blackmatrix7 独有规则（原文顺序）。
     两边动作都是 REJECT，无策略冲突。
  3. [URL Rewrite] 两边取并集；与 [Rule] 中 URL-REGEX 文本完全相同的重写会被规则覆盖，剔除。
  4. [Map Local] 只可莉版有，整体保留。
  5. [MITM] 两边主机名取并集，排序输出。
安全：任一数据源抓取失败，或合并条数低于阈值（规则<150、重写<15、MITM<15），非零退出且不改输出文件。
"""
import re
import sys
import urllib.request

KELI_URL = "https://raw.githubusercontent.com/gys619/surge-tools/main/modules/Block_HTTPDNS.sgmodule"
B7_URL = "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rewrite/Surge/BlockHTTPDNS/BlockHTTPDNS.sgmodule"
OUT = "BlockHTTPDNS-Combined.sgmodule"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "httpdns-sync"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def sections(text):
    secs, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^\[(.+)\]\s*$", line.strip())
        if m:
            cur = m.group(1).strip()
            secs.setdefault(cur, [])
        elif cur is not None:
            secs[cur].append(line)
    return secs


def entries(lines):
    return [l.rstrip() for l in lines if l.strip() and not l.strip().startswith("#")]


def main():
    try:
        keli = sections(fetch(KELI_URL))
        b7 = sections(fetch(B7_URL))
    except Exception as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1

    # [General]
    general = [l for l in entries(b7.get("General", [])) if "force-http-engine-hosts" in l]
    if not general:
        print("force-http-engine-hosts missing", file=sys.stderr)
        return 1

    # [Rule]
    k_rules = entries(keli.get("Rule", []))
    b_rules = entries(b7.get("Rule", []))
    and_rules = [r for r in k_rules if r.startswith("AND,")]
    rest_k = [r for r in k_rules if not r.startswith("AND,")]
    seen, rules = set(), []
    for r in and_rules + rest_k + b_rules:
        if r not in seen:
            seen.add(r)
            rules.append(r)

    # [URL Rewrite]：并集；剔除被同文本 URL-REGEX 规则覆盖的条目
    rule_regexes = set()
    for r in rules:
        m = re.match(r'^URL-REGEX,"(.*)",', r)
        if m:
            rule_regexes.add(m.group(1))
    rewrites, seen_rw = [], set()
    for rw in entries(keli.get("URL Rewrite", [])) + entries(b7.get("URL Rewrite", [])):
        pat = rw.split(" - ")[0].strip().strip('"')
        if pat in rule_regexes or pat in seen_rw:
            continue
        seen_rw.add(pat)
        rewrites.append(rw)

    # [Map Local]
    map_local = entries(keli.get("Map Local", []))

    # [MITM]
    def mitm_hosts(sec):
        hosts = []
        for l in entries(sec.get("MITM", [])):
            if "hostname" in l:
                hosts += [h.strip() for h in l.split("=", 1)[1].replace("%APPEND%", "").split(",") if h.strip()]
        return hosts
    mitm = sorted(set(mitm_hosts(keli)) | set(mitm_hosts(b7)))

    if len(rules) < 150 or len(rewrites) < 15 or len(mitm) < 15:
        print(f"counts too low: rules={len(rules)} rewrites={len(rewrites)} mitm={len(mitm)}", file=sys.stderr)
        return 1

    out = []
    out.append("#!name=BlockHTTPDNS 合并版（可莉 × blackmatrix7）")
    out.append("#!desc=拦截 App 内置 HTTPDNS，强制走 Surge 的 DNS 框架。合并可莉「HTTPDNS拦截器」（规则全）与 blackmatrix7 BlockHTTPDNS（引擎层 force-http-engine-hosts + 字节/火山等独有条目）。由 sync.py 自动合并，每日自动同步两个上游。")
    out.append(f"#!rule={len(rules)}")
    out.append(f"#!rewrite={len(rewrites)}")
    out.append(f"#!maplocal={len(map_local)}")
    out.append(f"#!mitm={len(mitm)}")
    out.append("")
    out.append("[General]")
    out += general
    out.append("")
    out.append("[Rule]")
    out += rules
    out.append("")
    out.append("[URL Rewrite]")
    out += rewrites
    out.append("")
    out.append("[Map Local]")
    out += map_local
    out.append("")
    out.append("[MITM]")
    out.append("hostname = %APPEND% " + ",".join(mitm))
    out.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"OK rules={len(rules)} rewrites={len(rewrites)} maplocal={len(map_local)} mitm={len(mitm)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
