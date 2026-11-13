# Safari 百度超级搜索

自研模块，仿墨鱼 Q-Search 的命令体系，但触发引擎换成百度：

- 前提：Safari 默认搜索引擎设为**百度**，启用本模块。
- 地址栏输入「命令+空格+关键词」或「关键词+空格+命令」直达目标站；不带命令不拦截，照常百度搜索。
- 命令：gg 谷歌、gh GitHub、by 必应、yd 有道词典、trc 谷歌译中、zh 知乎、wb 微博、db 豆瓣、tw X、yt YouTube、bli 哔哩哔哩、jd 京东 App、tb 淘宝 App（共 13 个，每个含前后两种写法）。
- 正则兼容百度搜索链接的常见形态：www/m 站、/s 与 /baidu 路径、wd/word 参数、参数前可带 ie=utf-8 等。若某 iOS 版本的链接格式不命中，命令不触发（仅普通百度搜索），把 Surge 日志里的实际链接发来即可适配。

安装：

```
https://raw.githubusercontent.com/lidalong112/ios_rule_script/master/script/baidu-search/BaiduSearch.sgmodule
```

本模块为手工维护，无上游同步任务；增删命令直接改 [URL Rewrite] 里对应两行（前缀/后缀各一）。
