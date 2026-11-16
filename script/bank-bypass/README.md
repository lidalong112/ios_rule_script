# 银行直连（跳过代理）BankBypass

让银行类 App 的流量绕过代理、直连官方服务器，避免银行 App 因代理/MITM 报网络异常或拒绝登录。

## 原理

iOS 版 Surge 无法按 App 排除流量（PROCESS-NAME 仅 Mac 可用），故按银行官方域名 `DOMAIN-SUFFIX` 全量直连。银行域名默认不在其他模块的 MITM 列表内，不会被解密，本模块只负责直连。

## 内容（28 条）

- 央行 / 银联体系：pbc.gov.cn、unionpay.com、unionpayintl.com、chinaums.com、nucc.cn
- 政策性银行：国开行、农发行、进出口银行
- 国有大行：工、建、农、中、交、邮储
- 股份制银行：招行、浦发、中信、光大、民生、兴业、广发、华夏、浙商、渤海、平安
- 地方银行（德州）：德州银行 dzbchina.com；德州农商银行无独立域名，走山东省农村信用社联合社统一平台 sdnxs.com / sdrcu.com

## 使用

把本模块放在 Surge 模块列表**最底部**（越靠下优先级越高），保证 DIRECT 先于去广告模块的拦截命中。手工维护，无自动同步；需要增加银行时编辑本文件即可。
