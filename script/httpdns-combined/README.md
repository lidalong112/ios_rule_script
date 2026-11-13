# BlockHTTPDNS 合并版（可莉 × blackmatrix7）

把两个 HTTPDNS 拦截模块合成一个，装这一个就够，不用再同时装原版：

- **可莉「HTTPDNS拦截器」**（可莉 + VirgilClyne，插件 2026-07-04）：规则最全，169 条合并规则里 146 条出自它，含嘀嗒出行的 DIRECT 例外（AND 规则置顶）、4 条 Map Local。
- **blackmatrix7 BlockHTTPDNS**（2025-06-06）：独有 `[General] force-http-engine-hosts`（引擎层拦腾讯 HTTPDNS，规则层做不到）+ 23 条独有规则（火山 volcengineapi、httpdns.pro 后缀、20 个独有 IP 等）+ 多数 IP 型重写。

合并计数：规则 169、URL 重写 22、Map Local 4、MITM 21。合并细则见 sync.py 顶部注释。
注：blackmatrix7 的 MITM 里有一条上游原文的笔误地址 `182.256.116.116`（256 不是合法 IP 段），按原文保留，无实际作用也无害。

## 安装

Surge → 模块 → 安装新模块，粘贴：

```
https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/httpdns-combined/BlockHTTPDNS-Combined.sgmodule
```

装了这个就不要再同时启用可莉原版或 blackmatrix7 原版，避免重复拦截。

## 自动同步

`sync.py` 每次从两个上游重新合并：可莉版经 GitHub 镜像 gys619/surge-tools 获取（kelee.one 屏蔽机房 IP，Actions 直连不了原站），blackmatrix7 版直取上游仓库。任一源抓取失败或条数异常就报错退出、不动模块文件。由 `.github/workflows/sync-httpdns.yml` 每日北京时间 05:20 自动运行，有变化才提交。

注意：嘀嗒出行的两条例外规则依赖 URL+UA 组合判断，若你不用嘀嗒出行，删掉 [Rule] 最前两条 AND 规则即可，不影响其余拦截。
