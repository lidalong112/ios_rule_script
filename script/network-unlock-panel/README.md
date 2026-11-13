# Surge 面板：网络信息与解锁检测

文件：
- `network-unlock-panel.js` —— 面板脚本本体（已通过语法检查和模拟运行测试）
- `network-unlock.sgmodule` —— 模块文件，含 [Panel] + [Script] 段

## 面板显示什么
- 节点出口 IP：IP、国家/城市（旗帜）、ASN/运营商、时区、当前策略组选择
  - IP 查询显式走 argument 指定的策略组（默认 `节点选择`），测的就是这个出口
- 本地网络 / 接口：接口名、Wi-Fi SSID/BSSID 或蜂窝运营商/制式、IPv4/网关、IPv6、DNS、设备与 Surge 版本（来自 $network / $environment）
- 节点 IP 纯净度：主数据源 proxycheck.io（免 key）的风险分 + 代理/VPN 标记 + IP 类型（住宅/商业/机房），再用 ip-api 的 proxy/hosting/mobile 交叉验证。面板的「纯净度 X 分」是按这两项综合换算的：基础 100 - 风险分，代理 -30、VPN -20、机房 -25、商业 -10，并把扣分明细（类型、风险分、各标记）都显示出来，不是官方分数。proxycheck 免 key 额度约 100 次/天，所以模块的自动刷新间隔设为 3600 秒（1 小时），平时用右上角手动刷新；不要把间隔改回几分钟，否则一天内打开策略页几次就可能把额度用完，纯净度那段会显示「检测失败」
- 流媒体解锁：Netflix（双片源法：完整解锁 / 仅自制剧 / 未解锁）、Disney+、YouTube Premium（带地区）、TikTok（带地区）
- AI 解锁：ChatGPT/OpenAI（API 返回 401=地区可用，403=地区封锁，并用 chatgpt.com trace 显示出口地区）、Claude、Gemini
  - 注意：Claude 对脚本请求经常回 Cloudflare 校验的 403，那不是地区封锁，脚本会显示「无法判定（被 Cloudflare 拦截）」而不是误报未解锁

流媒体 / AI 检测不指定 policy，按你现有配置的规则走各自策略组（奈飞走奈飞组、AI 走智能助理组等），和你实际打开这些 App 时走的路径一致。如果你想全部强制走同一个节点，把脚本里对应 get() 的 opts.policy 设上，或告诉 Muse 改一版。

## 安装（iOS，二选一）

方法 A：加到现有配置（推荐，配合 Surge-CN-X-v2 使用）
1. 在 Surge 里打开「脚本 > 新建脚本」，把 `network-unlock-panel.js` 全文粘进去，保存为 `network-unlock-panel.js`。
2. 编辑你正在用的配置，在末尾加上 sgmodule 里的 [Panel] 和 [Script] 两段（不要重复加已有的段头，把两行分别并入已有的 [Panel] / [Script] 段）。
3. 回到策略选择页，就能看到「网络信息与解锁检测」面板，点刷新。

方法 B：模块导入（自带在线脚本，不用先存本地 JS）
1. Surge > 模块 > 安装模块，粘贴在线模块链接 `https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/network-unlock-panel/network-unlock.sgmodule` 并启用。
2. 回到策略选择页，就能看到「网络信息与解锁检测」面板，点刷新。

## 改策略组名
如果你主策略组不叫「节点选择」，改 [Script] 那行的 `argument=你的组名`，或改 sgmodule 里的同一处。

## 超时说明
脚本整体超时在配置里设为 30 秒（手册默认只有 5 秒，不够跑完 8 项检测），脚本内部单项请求超时 8 秒、整体 25 秒兜底出结果。
