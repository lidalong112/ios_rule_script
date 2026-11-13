# anti-AD 广告域名集（模块版）

把 privacy-protection-tools/anti-AD 的 Surge 域名集包成一个可开关的模块，内容只有一行：

```
DOMAIN-SET,https://anti-ad.net/surge2.txt,REJECT,extended-matching,update-interval=86400
```

- 域名集本体（10 万+ 条）由 Surge 直接从 anti-ad.net 拉取，每 24 小时自动更新，**不需要仓库侧的同步任务**，本目录也没有 sync.py。
- `extended-matching`：同时用 TLS SNI 与 HTTP Host 匹配，能拦住用 IP 直连但带广告域名的请求。
- 没加 `pre-matching`：避免它越过其他模块的例外放行（如 BlockAdvertisers 里字节 tnc 的 DIRECT 例外）。模块顺序建议把本模块放在 BlockAdvertisers **上方**（Surge 里越靠下优先级越高）。
- anti-AD 风格偏激进，个别 App 功能异常时，先停用本模块排查。

## 安装

```
https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/anti-ad/Anti-AD.sgmodule
```
