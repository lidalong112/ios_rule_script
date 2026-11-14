# 外链接跳转Turrit（Redirect2Turrit 增强版）

在浏览器或其它 App 里点到 Telegram 外部链接时，按链接类型拆开处理，307 跳到 Turrit 客户端打开，而不是落到 Safari 的网页版。链接分类与目标形式依据 Telegram 官方深链文档（core.telegram.org/api/links）。

基于墨鱼（ddgksf2013）的 Redirect2Turrit 一行版扩展：原版只有一条兜底规则，把 `t.me/` 后面的一切当作 domain 传递，帖子链接、邀请链接、私有频道链接都会传错；本版按类型拆成 15 条（顺序即优先级，首中即停，兜底排最后）：

| 链接形式 | 跳转 |
|---|---|
| `t.me/c/频道ID/帖子ID`、`t.me/c/频道ID/话题ID/帖子ID`（私有频道/群） | `turrit://privatepost?channel=ID&post=帖子ID`（带话题时加 `&thread=`） |
| `t.me/频道/帖子ID`、`t.me/频道/话题ID/帖子ID`（公开，含论坛话题） | `turrit://resolve?domain=频道&post=帖子ID`（带话题时加 `&thread=`） |
| `t.me/s/频道`、`t.me/s/频道/帖子ID`（预览页） | `turrit://resolve?domain=频道`（带帖子时加 `&post=`） |
| `t.me/+手机号`（纯数字） | `turrit://resolve?phone=手机号` |
| `t.me/+hash`、`t.me/joinchat/hash`（邀请） | `turrit://join?invite=hash` |
| `t.me/share/url?...` | `turrit://msg_url?...` |
| `t.me/proxy?...` | `turrit://proxy?...` |
| `t.me/addstickers/包名`、`t.me/addemoji/包名` | `turrit://addstickers?set=包名` / `addemoji` |
| `t.me/名字?start=xx` 等带参数链接 | 参数透传给 resolve |
| `t.me/名字`（兜底） | `turrit://resolve?domain=名字` |

覆盖域名 `t.me`、`telegram.me`、`telegram.dog`，MITM 三个域名。已用模拟请求逐条验证 20 种链接（含旧版 11 种回归 + 新增 9 种）的命中与替换结果，全部符合预期。

防误伤设计：通用帖子/参数/兜底规则都带保留段负向前瞻（c、s、share、proxy、joinchat、addstickers、addemoji、addlist、contact、m、boost），兜底收紧为单段锚定。未覆盖的保留路径（如 `contact/`、`addlist/`、`m/`、`t.me/c/频道ID` 首页）不再被误跳成错误的 resolve，而是原样在浏览器打开。

说明：纯 `resolve` 形式是原作者验证过的；`privatepost`、`post`、`join`、`phone`、`proxy`、`msg_url` 等扩展形式按 Telegram 官方 `tg://` 规范编写，Turrit 作为 TG 客户端大概率同样支持，未在真机逐项验证。想跳官方 Telegram，把模块里的 `turrit://` 全部替换为 `tg://` 即可。不需要的链接类型整行删掉即可。

前提：机子上装有 Turrit 本体。手工维护，无自动同步。

固定地址：https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/redirect2turrit/Redirect2Turrit.sgmodule
