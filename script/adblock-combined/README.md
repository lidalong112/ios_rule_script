# 去广告合集模块（墨鱼去开屏 + 可莉过滤器）

把两个去广告模块合并成一个 Surge 模块，并**自动同步上游**：

- **墨鱼去开屏 V2.0**（@ddgksf2013）：专去 App 开屏广告，400 余应用。
  上游是 Quantumult X 重写文件 `https://ddgksf2013.top/rewrite/StartUpAds.conf`，由 `sync.py` 按固定规则转成 Surge 写法后合并。
- **可莉广告过滤器**（可莉，自用向）：小米系、有道词典、拼多多等约 30 个 App + 常用广告 SDK 域名拦截。
  源站 kelee.one 对机房 IP（含 GitHub Actions）是 Cloudflare 硬拦截，无法直抓 Loon 插件，
  故可莉部分以 GitHub 镜像 `gys619/surge-tools` 中同一插件的 Script Hub 转换版为同步源。
- **[Script] 的 27 个远程脚本**不在模块文件里，Surge 运行时直接从作者 GitHub 拉取，天然与上游同步，不经过本仓库。

## 在 Surge 里使用

模块链接（固定不变，内容由 Actions 每天同步）：

```
https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/adblock-combined/AdBlock-Combined.sgmodule
```

在 Surge 里添加模块并启用，再开启 MITM、信任 Surge 的 CA 证书即可生效。
装了这个就不要再装墨鱼 / 可莉的原版模块，会重复冲突。

## 自动同步怎么运作

- `.github/workflows/sync-adblock.yml`：每天北京时间 04:35 自动运行（也可手动触发），
  运行 `sync.py` 拉上游 → 转换 → 按合并规则重新生成 `AdBlock-Combined.sgmodule` → 有变化才提交。
- 合并规则（同目标取舍、联通 accountListData 的处理等）写在 `sync.py` 顶部注释和模块文件头里。
- 任一上游拉取失败或内容异常，脚本非零退出且不改文件，Actions 会显示失败，不会提交坏内容。
- 本地手动同步：`python3 sync.py`（可加 `--moyu-file/--keli-file` 用本地文件离线测试）。

## 已知事项

- `reject-200` / `reject-dict` 在 Surge 官方手册的 URL Rewrite 章节只列了 `reject`，
  但 blackmatrix7 等上游 Surge 模块同样在用；如你的 Surge 报错，可把模块里的 reject-200 整体替换为 reject。
- 银行类、抖音等无法 MITM 的应用按墨鱼作者说明无效。
- 墨鱼源文件里 1 条 TestFlight 改 storefrontId 的 request-body 与去广告无关，Surge 无法原样表达，未收录。
