# 广告平台拦截器（可莉 BlockAdvertisers）

可莉的「广告平台拦截器」：在广告平台/SDK 域名层拦截，是其他去广告插件的依赖层。覆盖腾讯、字节、快手、百度、阿里妈妈、友盟、个推、极光等国内广告平台与 Google、AppLovin、Unity、AppsFlyer 等海外平台。

内容：规则 330 条（DOMAIN-SUFFIX 195、DOMAIN 118、DOMAIN-KEYWORD 12、AND 4、IP-CIDR 1，多数带 pre-matching + extended-matching）、URL 重写 4（拼多多 DSP）、MITM 3。含一条字节 tnc 配置域名的 AND DIRECT 放行，避免误杀剪映/抖音正常配置。

## 安装

```
https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/block-advertisers/BlockAdvertisers.sgmodule
```

按作者要求，这个模块要在 Surge 的模块列表里**排在其他去广告模块前面**（拖到 AdBlock-Combined 上方）。

## 自动同步

原插件在 kelee.one（屏蔽机房 IP，Actions 直连不了），sync.py 改从 Repcz/Tool 仓库维护的 Kelee Surge 转换版同步，并做两处确定性修正：URL Rewrite 的 " _ reject" 残留分隔符改为 " - reject"；AND 规则括号内空格去除。由 `.github/workflows/sync-block-advertisers.yml` 每日北京时间 05:35 自动运行，源抓取失败或规则数异常就报错不动文件。
