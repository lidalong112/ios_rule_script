# Rules And Scripts

各平台的分流规则、复写规则及自动化脚本。

**本仓库说明**：这是 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 的 fork，每日自动同步上游规则库；同时在 `script/` 下维护 8 个自研 / 合并的 Surge 模块（去广告、HTTPDNS 拦截、网络面板、银行直连等），每个模块都有固定安装地址，部分模块每日自动同步各自的上游。

> **⚠️ 强调：本文档与本仓库的自研模块，全部由 AI 编写。**
> 包括本 README 的文字、各自研模块的合并 / 转换代码与说明文档，均由 AI（Muse）生成，仓库主只负责提出需求与验收。使用前请自行核验内容，AI 生成内容不保证完全准确；上游规则库与上游脚本为原作者作品，不在此列。

## 目录

- [自研模块](#自研模块)
- [上游规则库](#上游规则库)
- [上游脚本](#上游脚本)
- [自动化同步](#自动化同步)
- [模块排序建议](#模块排序建议)
- [特别声明](#特别声明)
- [感谢](#感谢)

## 自研模块

以下模块均为 Surge 模块，点击「安装」即为固定 raw 地址，可直接在 Surge 中添加。带自动同步的模块见 [自动化同步](#自动化同步)，其余为手工维护。

| 模块 | 说明 | 安装 |
| --- | --- | --- |
| [网络解锁面板](https://github.com/lidalong112/ios_rule_script/tree/master/script/network-unlock-panel) | 面板显示出口 IP / 位置 / 运营商、Netflix / Disney+ / YouTube / TikTok 与 ChatGPT / Claude / Gemini 解锁检测、IP 纯净度、本地网络信息 | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/network-unlock-panel/network-unlock.sgmodule) |
| [去广告合集](https://github.com/lidalong112/ios_rule_script/tree/master/script/adblock-combined) | 墨鱼去开屏 V2.0 与可莉去广告合并，覆盖 400+ App 的开屏 / 弹窗广告 | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/adblock-combined/AdBlock-Combined.sgmodule) |
| [HTTPDNS 拦截合并版](https://github.com/lidalong112/ios_rule_script/tree/master/script/httpdns-combined) | 可莉 HTTPDNS 拦截器与 blackmatrix7 BlockHTTPDNS 合并，169 条规则，强制 App 走 Surge 的 DNS 框架 | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/httpdns-combined/BlockHTTPDNS-Combined.sgmodule) |
| [广告平台拦截器](https://github.com/lidalong112/ios_rule_script/tree/master/script/block-advertisers) | 可莉出品，330 条规则拦截腾讯 / 字节 / 快手等百余家广告平台（含 Mob、极光等 DIRECT 放行例外，务必垫底排序） | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/block-advertisers/BlockAdvertisers.sgmodule) |
| [anti-AD 域名集](https://github.com/lidalong112/ios_rule_script/tree/master/script/anti-ad) | privacy-protection-tools 的 10 万+ 广告 / 追踪域名集，以 DOMAIN-SET 远程引用，Surge 每日自动拉取上游 | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/anti-ad/Anti-AD.sgmodule) |
| [百度超级搜索](https://github.com/lidalong112/ios_rule_script/tree/master/script/baidu-search) | Safari 默认引擎设为百度时，地址栏输入 gg / gh 等 13 个命令直达 Google、GitHub、Bing、知乎、B 站等站点 | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/baidu-search/BaiduSearch.sgmodule) |
| [Telegram 跳转 Turrit](https://github.com/lidalong112/ios_rule_script/tree/master/script/redirect2turrit) | 把 t.me / telegram.me 链接 307 跳转到 Turrit 打开，覆盖帖子、私有频道、邀请、代理等 15 种链接形态 | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/redirect2turrit/Redirect2Turrit.sgmodule) |
| [银行直连](https://github.com/lidalong112/ios_rule_script/tree/master/script/bank-bypass) | 28 条银行 / 银联域名直连规则，让银行 App 跳过代理（含德州银行、德州农商银行） | [安装](https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/bank-bypass/BankBypass.sgmodule) |

## 上游规则库

**我们并不生产规则，我们只是开源规则的搬运工。**

- 分流规则：https://github.com/lidalong112/ios_rule_script/tree/master/rule
- 复写规则：https://github.com/lidalong112/ios_rule_script/tree/master/rewrite
- 图标库：https://github.com/lidalong112/ios_rule_script/tree/master/icon

所有规则数据都来自互联网，感谢开源规则项目作者的辛勤付出。

## 上游脚本

| 脚本 | 介绍 | 框架 | 维护状态 |
| --- | --- | --- | --- |
| [什么值得买](https://github.com/lidalong112/ios_rule_script/tree/master/script/smzdm) | 什么值得买任务和去广告 | MagicJS 2/3 | 正常 |
| [百度贴吧](https://github.com/lidalong112/ios_rule_script/tree/master/script/tieba) | 带重试功能的贴吧签到，提高签到成功率 | MagicJS 3 | 正常 |
| [开屏去广告](https://github.com/lidalong112/ios_rule_script/tree/master/script/startup) | 通过脚本去除缓存到本地的APP开屏广告 | MagicJS 3 | 正常 |
| [慢慢买](https://github.com/lidalong112/ios_rule_script/tree/master/script/manmanbuy) | 每日自动签到 | MagicJS 2 | 正常 |
| [叮咚买菜](https://github.com/lidalong112/ios_rule_script/tree/master/script/dingdong) | 每日自动签到 | MagicJS 3 | 正常 |
| [Fa米家](https://github.com/lidalong112/ios_rule_script/tree/master/script/famijia) | 每日自动签到 | MagicJS 2 | 正常 |
| [Luka](https://github.com/lidalong112/ios_rule_script/tree/master/script/luka) | 每日自动签到 | MagicJS 2 | 正常 |
| [哲也同学](https://github.com/lidalong112/ios_rule_script/tree/master/script/zheye) | 之乎者也 | MagicJS 3 | 正常 |
| [Synology](https://github.com/lidalong112/ios_rule_script/tree/master/script/synology) | 群晖Download Station资源离线下载 | MagicJS 3 | 正常 |
| [AppleStore](https://github.com/lidalong112/ios_rule_script/tree/master/script/applestore) | AppleStore 商品库存监控 | MagicJS 3 | 暂停 |

### Quantumult X Gallery

部分脚本已配置为 Quantumult X Gallery。

地址：https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/gallery.json

### BoxJS

感谢 [@chouchoui](https://github.com/chouchoui) 为本项目添加 BoxJS 的订阅。

地址：https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/boxjs.json

### 外部资源

项目中资源来自互联网上其他开源项目（具体以不同目录的说明为准），这里主要进行一些整合和备份。对于此类资源，无法对使用过程中出现的任何问题进行解答，您需要联系原作者。

地址：https://github.com/lidalong112/ios_rule_script/tree/master/external

## 自动化同步

仓库由 GitHub Actions 每日自动维护（北京时间），无需手动更新：

| 工作流 | 时间 | 作用 |
| --- | --- | --- |
| Sync AdBlock Combined | 04:35 | 重新合并墨鱼 + 可莉去广告模块 |
| Sync Fork With Upstream | 05:05 | 同步 blackmatrix7 上游规则库 |
| Sync HTTPDNS Combined | 05:20 | 重新合并 HTTPDNS 拦截模块 |
| Sync BlockAdvertisers | 05:35 | 同步广告平台拦截器 |
| Reset Fork To Upstream | 手动 | 上游历史重写时一键对齐（休眠备用） |

## 模块排序建议

Surge 中模块**越靠下优先级越高**。自研模块推荐从上到下：

1. 网络解锁面板
2. HTTPDNS 拦截合并版
3. 去广告合集
4. anti-AD 域名集
5. 广告平台拦截器（其 DIRECT 放行例外需要最高优先级）
6. 银行直连（DIRECT 需赶在拦截规则之前命中）

## 特别声明

1. 本项目内所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布。
2. 编写本项目主要目的为学习和研究ES6，无法保证项目内容的合法性、准确性、完整性和有效性。
3. 本项目涉及的数据由使用的个人或组织自行填写，本项目不对数据内容负责，包括但不限于数据的真实性、准确性、合法性。使用本项目所造成的一切后果，与本项目的所有贡献者无关，由使用的个人或组织完全承担。
4. 本项目中涉及的第三方硬件、软件等，与本项目没有任何直接或间接的关系。本项目仅对部署和使用过程进行客观描述，不代表支持使用任何第三方硬件、软件。使用任何第三方硬件、软件，所造成的一切后果由使用的个人或组织承担，与本项目无关。
5. 本项目中所有内容只供学习和研究使用，不得将本项目中任何内容用于违反国家/地区/组织等的法律法规或相关规定的其他用途。
6. 所有基于本项目源代码，进行的任何修改，为其他个人或组织的自发行为，与本项目没有任何直接或间接的关系，所造成的一切后果亦与本项目无关。
7. 所有直接或间接使用本项目的个人和组织，应24小时内完成学习和研究，并及时删除本项目中的所有内容。如对本项目的功能有需求，应自行开发相关功能。
8. 本项目保留随时对免责声明进行补充或更改的权利，直接或间接使用本项目内容的个人或组织，视为接受本项目的特别声明。

## 感谢

以下排名不分先后

[@BaileyZyp](https://github.com/BaileyZyp)   [@Mazeorz](https://github.com/Mazeorz)   [@LuzMasonj](https://github.com/LuzMasonj)  [@chouchoui](https://github.com/chouchoui)  [@ypannnn](https://github.com/ypannnn)  [@echizenryoma](https://github.com/echizenryoma)  [@zirawell](https://github.com/zirawell)  [@urzz](https://github.com/urzz)  [@ASD-max](https://github.com/ASD-max)

本仓库自研模块另感谢：可莉（kelee）、墨鱼（ddgksf2013）、app2smile、Repcz、privacy-protection-tools（anti-AD）等作者的开源作品。
