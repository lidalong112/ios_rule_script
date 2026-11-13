#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdBlock-Combined 同步脚本：拉取上游、转换、合并，生成 AdBlock-Combined.sgmodule。

上游：
  1) 墨鱼去开屏 V2.0（Quantumult X 重写） https://ddgksf2013.top/rewrite/StartUpAds.conf
     -> 本脚本按固定规则转成 Surge 写法（reject 系列进 [URL Rewrite]，
        script-* 进 [Script]，response-body / jsonjq 进 [Body Rewrite]，
        host / host-suffix 进 [Rule]，hostname 进 [MITM]）。
  2) 可莉广告过滤器（Loon 插件经 Script Hub 转的 Surge 模块，GitHub 镜像）
     https://raw.githubusercontent.com/gys619/surge-tools/main/modules/Remove_ads_by_keli.sgmodule
     说明：kelee.one 对机房 IP（含 GitHub Actions）是 Cloudflare 硬拦截，无法直抓 .lpx，
     故可莉部分以上述 GitHub 镜像为同步源；墨鱼部分是作者源站直抓。
  3) [Script] 里的 27 个远程脚本不在本文件内，Surge 运行时直接从作者 GitHub 拉取，
     天然与上游同步，无需本脚本处理。

合并规则（与手工合并版一致）：
  - 各段去重（保留首次出现顺序，墨鱼在前、可莉在后；Map Local 只来自可莉）。
  - 同一广告接口两边都有时各留一份：站酷开屏 / 有道词典开屏 / cmgadx / 向日葵素材 /
    猫眼广告图 / qinlinad / 腾讯 exapp 留可莉 Map Local（返回 {} JSON），删墨鱼 reject-200；
    小米商城开屏 / 和风天气 / 美的 mddcloud / 小米商城 pageConfig 留墨鱼 reject-200，删可莉 Map Local。
  - 中国联通 accountListData：墨鱼正则摘掉该分支，只走可莉 Map Local 的精细版（清广告字段、留账户数据）。
  - 任一上游拉取失败或解析异常：非零退出且不改动输出文件，避免把坏内容提交上去。

用法：
  python3 sync.py [--out AdBlock-Combined.sgmodule]
                  [--moyu-url URL] [--keli-url URL]
                  [--moyu-file PATH] [--keli-file PATH]   # 本地文件覆盖，便于离线测试
"""
import argparse, os, re, sys, urllib.request
from datetime import date

MOYU_URL = "https://ddgksf2013.top/rewrite/StartUpAds.conf"
KELI_URL = "https://raw.githubusercontent.com/gys619/surge-tools/main/modules/Remove_ads_by_keli.sgmodule"

DROP_MOYU_REWRITE_KEYS = [
    'api\\.zcool\\.com\\.cn', 'cdke\\.youdao\\.com', 'cdn\\.cmgadx\\.com\\/sdk\\/pool',
    'client-api-v2\\.oray\\.com', 'p0\\.pipi\\.cn\\/mediaplus',
    'qadx\\.qinlinad\\.com', 'us\\.l\\.qq\\.com\\/exapp',
]
DROP_KELI_MAP_KEYS = [
    'api\\.m\\.mi\\.com\\/v\\d\\/app\\/start', 'hfapp-service\\.qweather\\.net',
    'mob\\.mddcloud\\.com\\.cn\\/adApi', 'shopapi\\.io\\.mi\\.com',
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Surge"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "strict")

def dedupe(lines):
    seen, out = set(), []
    for l in lines:
        if l not in seen:
            seen.add(l); out.append(l)
    return out

# ---------------- 墨鱼 QX -> Surge ----------------
def convert_moyu(text):
    rule, rewrite, body, script, mitm = [], [], [], [], []
    skipped = []
    script_no = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("//") or line.startswith("#") or line.startswith(";"):
            continue  # 注释/作者禁用行（# 或 ; 开头）按原意不启用
        if line.startswith("hostname"):
            mitm = [h.strip() for h in line.split("=", 1)[1].split(",") if h.strip()]
            continue
        m = re.match(r"^host(?:-suffix)?\s*,\s*([^,]+),\s*(\w+)$", line)
        if m:
            kind = "DOMAIN-SUFFIX" if line.startswith("host-suffix") else "DOMAIN"
            rule.append(f"{kind},{m.group(1).strip()},{m.group(2).strip().upper()}")
            continue
        m = re.match(r"^(\S+)\s+url\s+(.+)$", line)
        if not m:
            skipped.append(line); continue
        pattern, rest = m.group(1), m.group(2)
        if rest.startswith(("reject-200", "reject-img", "reject-dict", "reject-array", "reject-video")) or rest == "reject":
            action = rest.split()[0]
            rewrite.append(f"{pattern} - {action}")
        elif rest.startswith("script-response-body "):
            script_no += 1
            url = rest.split(" ", 1)[1].strip()
            name = os.path.basename(url).rsplit(".js", 1)[0]
            script.append(f"startup-{script_no:02d}-{name} = type=http-response,pattern={pattern.replace(chr(44), chr(92)+chr(44))},script-path={url},requires-body=true")
        elif rest.startswith("script-response-header "):
            script_no += 1
            url = rest.split(" ", 1)[1].strip()
            name = os.path.basename(url).rsplit(".js", 1)[0]
            script.append(f"startup-{script_no:02d}-{name} = type=http-response,pattern={pattern.replace(chr(44), chr(92)+chr(44))},script-path={url},requires-body=false")
        elif rest.startswith("script-analyze-echo-response "):
            script_no += 1
            url = rest.split(" ", 1)[1].strip()
            name = os.path.basename(url).rsplit(".js", 1)[0]
            script.append(f"# QX script-analyze-echo-response -> Surge http-response，未验证，需实测")
            script.append(f"startup-{script_no:02d}-{name} = type=http-response,pattern={pattern.replace(chr(44), chr(92)+chr(44))},script-path={url},requires-body=true")
        elif rest.startswith("response-body "):
            tail = rest[len("response-body "):]
            parts = tail.split(" response-body ", 1)
            if len(parts) != 2:
                skipped.append(line); continue
            body.append(f"http-response {pattern} {parts[0]} {parts[1]}")
        elif rest.startswith("jsonjq-response-body "):
            body.append(f"http-response-jq {pattern} {rest[len('jsonjq-response-body '):]}")
        elif rest.startswith("request-body "):
            skipped.append(line)  # TestFlight storefrontId 改写：与去广告无关，Surge 无法原样表达
        else:
            skipped.append(line)
    return {"Rule": rule, "URL Rewrite": rewrite, "Body Rewrite": body,
            "Script": script, "MITM": dedupe(mitm)}, skipped

# ---------------- 解析现成 sgmodule（可莉镜像） ----------------
def parse_sgmodule(text):
    secs, cur = {}, None
    for raw in text.splitlines():
        l = raw.rstrip("\n")
        m = re.match(r"^\[(.+)\]\s*$", l)
        if m:
            cur = m.group(1); secs.setdefault(cur, []); continue
        if cur and l.strip() and not l.startswith("#"):
            secs[cur].append(l.strip())
    if "MITM" in secs:
        line = secs["MITM"][0]
        secs["MITM"] = [h.strip() for h in line.split("=", 1)[1].replace("%APPEND%", "").split(",") if h.strip()]
    return secs

# ---------------- 合并 ----------------
def merge(moyu, keli):
    moyu_rw, dropped_m = [], []
    for l in moyu["URL Rewrite"]:
        if any(k in l for k in DROP_MOYU_REWRITE_KEYS):
            dropped_m.append(l)
        elif "accountListData|get_client_adv" in l:
            moyu_rw.append(l.replace("(accountListData|get_client_adv|get_startadv)", "(get_client_adv|get_startadv)"))
        else:
            moyu_rw.append(l)
    keli_map, dropped_k = [], []
    for l in keli.get("Map Local", []):
        if any(k in l for k in DROP_KELI_MAP_KEYS):
            dropped_k.append(l)
        else:
            keli_map.append(l)
    out = {
        "Rule": dedupe(moyu["Rule"] + keli.get("Rule", [])),
        "URL Rewrite": dedupe(moyu_rw + keli.get("URL Rewrite", [])),
        "Body Rewrite": dedupe(moyu["Body Rewrite"] + keli.get("Body Rewrite", [])),
        "Map Local": dedupe(keli_map),
        "Script": dedupe(moyu["Script"]),
        "MITM": dedupe(moyu["MITM"] + keli.get("MITM", [])),
    }
    return out, dropped_m, dropped_k

HEADER = """#!name=去广告合集（墨鱼去开屏 + 可莉过滤器）
#!desc=墨鱼去开屏 V2.0（@ddgksf2013）+ 可莉广告过滤器 · 由仓库 sync.py 自动同步上游生成，最近生成 {today}
#!author=@ddgksf2013、可莉
# 本文件由 script/adblock-combined/sync.py 自动生成，请勿手改（改了也会被下一次同步覆盖）。
# 上游：墨鱼 {moyu_url}（直抓转换）；可莉经 GitHub 镜像 {keli_url}（kelee.one 拦截机房 IP，无法直抓）。
# [Script] 的远程脚本由 Surge 运行时直接从作者 GitHub 拉取，与上游天然同步。
# 合并计数：Rule {n_rule} · URL Rewrite {n_rewrite} · Body Rewrite {n_body} · Map Local {n_map} · Script {n_script} · MITM {n_mitm}
# 同目标取舍：站酷/有道开屏、cmgadx、向日葵、猫眼图、qinlinad、腾讯 exapp 留可莉 Map Local（删墨鱼 {n_dm} 条）；
#   小米商城开屏、和风天气、美的 mddcloud、商城 pageConfig 留墨鱼 reject-200（删可莉 {n_dk} 条）；
#   联通 accountListData 只走可莉 Map Local（墨鱼正则已摘该分支）。
# 注意：不要再同时安装墨鱼/可莉原版模块；生效需开 MITM 并信任 Surge CA；
#   reject-200/reject-dict 若被 Surge 报错，可整体替换为 reject；银行类、抖音等无法 MITM 的应用无效。
"""

def render(secs, dropped_m, dropped_k):
    parts = [HEADER.format(today=date.today().isoformat(), moyu_url=MOYU_URL, keli_url=KELI_URL,
                            n_rule=len(secs["Rule"]), n_rewrite=len(secs["URL Rewrite"]),
                            n_body=len(secs["Body Rewrite"]), n_map=len(secs["Map Local"]),
                            n_script=len([l for l in secs["Script"] if not l.startswith("#")]), n_mitm=len(secs["MITM"]),
                            n_dm=len(dropped_m), n_dk=len(dropped_k))]
    for name in ["Rule", "URL Rewrite", "Body Rewrite", "Map Local", "Script"]:
        parts.append(f"[{name}]")
        parts.extend(secs[name])
        parts.append("")
    parts.append("[MITM]")
    parts.append("hostname = %APPEND% " + ", ".join(secs["MITM"]))
    parts.append("")
    return "\n".join(parts)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "AdBlock-Combined.sgmodule"))
    ap.add_argument("--moyu-url", default=MOYU_URL)
    ap.add_argument("--keli-url", default=KELI_URL)
    ap.add_argument("--moyu-file")
    ap.add_argument("--keli-file")
    a = ap.parse_args()
    try:
        moyu_text = open(a.moyu_file, encoding="utf-8").read() if a.moyu_file else fetch(a.moyu_url)
        keli_text = open(a.keli_file, encoding="utf-8").read() if a.keli_file else fetch(a.keli_url)
    except Exception as e:
        print(f"ERROR: 拉取上游失败：{e}", file=sys.stderr); return 1
    if "StartUpAds" not in moyu_text and "墨鱼" not in moyu_text:
        print("ERROR: 墨鱼上游内容异常（疑似拦截页）", file=sys.stderr); return 1
    if "[MITM]" not in keli_text or "可莉" not in keli_text:
        print("ERROR: 可莉镜像内容异常", file=sys.stderr); return 1
    moyu, skipped = convert_moyu(moyu_text)
    keli = parse_sgmodule(keli_text)
    secs, dm, dk = merge(moyu, keli)
    if len(secs["URL Rewrite"]) < 400 or len(secs["MITM"]) < 400 or len(secs["Script"]) < 20:
        print(f"ERROR: 合并结果计数异常：{ {k: len(v) for k, v in secs.items()} }", file=sys.stderr); return 1
    content = render(secs, dm, dk)
    old = open(a.out, encoding="utf-8").read() if os.path.exists(a.out) else None
    if old == content:
        print("无变化，未写入。")
    else:
        open(a.out, "w", encoding="utf-8").write(content)
        print(f"已写入 {a.out}")
    print({k: len(v) for k, v in secs.items()}, "skipped:", len(skipped), "dropped:", len(dm), "+", len(dk))
    return 0

if __name__ == "__main__":
    sys.exit(main())
