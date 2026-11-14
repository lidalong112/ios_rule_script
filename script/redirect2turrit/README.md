# 外链接跳转Turrit（Redirect2Turrit 增强版）

在浏览器或其它 App 里点到 Telegram 外部链接时，按链接类型拆开处理，307 跳到 Turrit 客户端打开，而不是落到 Safari 的网页版。

基于墨鱼（ddgksf2013）的 Redirect2Turrit 一行版扩展：原版只有一条兜底规则，把 `t.me/` 后面的一切当作 domain 传递，帖子链接、邀请链接会传错；本版按类型拆成 11 条（顺序即优先级，首中即停，兜底排最后）：

| 链接形式 | 跳转 |
|---|---|
| `t.me/频道/123`、`t.me/s/频道/123` | `turrit://resolve?domain=频道&post=123` |
| `t.me/s/频道` | `turrit://resolve?domain=频道` |
| `t.me/+hash`、`t.me/joinchat/hash` | `turrit://join?invite=hash` |
| `t.me/share/url?...` | `turrit://msg_url?...` |
| `t.me/proxy?...` | `turrit://proxy?...` |
| `t.me/addstickers/包名`、`t.me/addemoji/包名` | `turrit://addstickers?set=包名` / `addemoji` |
| `t.me/名字?start=xx` | 参数透传给 resolve |
| `t.me/名字`（兜底，即原版那条） | `turrit://resolve?domain=名字` |

覆盖域名 `t.me`、`telegram.me`、`telegram.dog`，MITM 三个域名。已用模拟请求逐条验证 11 种链接的命中与替换结果。

说明：纯 `resolve` 形式是原作者验证过的；`post`、`join`、`proxy`、`msg_url` 等扩展形式按 Telegram 官方 `tg://` scheme 规范编写，Turrit 作为 TG 客户端大概率同样支持，未在真机逐项验证。想跳官方 Telegram，把模块里的 `turrit://` 全部替换为 `tg://` 即可。不需要的链接类型整行删掉即可。

前提：机子上装有 Turrit 本体。手工维护，无自动同步。

固定地址：https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/redirect2turrit/Redirect2Turrit.sgmodule
