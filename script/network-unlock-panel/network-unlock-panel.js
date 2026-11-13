// ============================================================
// Surge 面板：节点 IP / 网络 / 接口信息 + 流媒体 & AI 解锁检测
// 作者：Muse for mice | 按 Surge 官方手册 scripting / panel API 编写
// 用法见同目录的 network-unlock.sgmodule 和 README 说明
//
// 可选参数 argument：填你的主策略组名（默认：节点选择）
// IP 信息查询会显式走这个策略组，测的就是这个出口；
// 流媒体 / AI 检测不指定 policy，按你配置的规则走各自的策略组
// （奈飞走奈飞组、AI 走智能助理组），这才是你实际打开 App 时的路径。
// ============================================================

var GROUP = (typeof $argument!== "undefined" && $argument)? String($argument): "节点选择";
var UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1";
var TIMEOUT = 8;

function get(url, opts) {
opts = opts || {};
return new Promise(function (resolve) {
var req = {
url: url,
headers: { "User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"},
timeout: TIMEOUT,
"auto-redirect": opts.redirect!== false
};
if (opts.policy) req.policy = opts.policy;
try {
$httpClient.get(req, function (error, response, data) {
if (error) resolve({ ok: false, error: String(error), status: 0, headers: {}, body: ""});
else resolve({ ok: true, status: response.status, headers: response.headers || {}, body: data || ""});
});
} catch (e) {
resolve({ ok: false, error: String(e), status: 0, headers: {}, body: ""});
}
});
}

function flag(code) {
if (!code || code.length!== 2) return "🌐";
code = code.toUpperCase();
// UK 是 Cloudflare 等常用写法，旗帜按 GB 显示
var cc = code === "UK"? "GB": code;
return String.fromCodePoint(0x1F1E6 + cc.charCodeAt(0) - 65, 0x1F1E6 + cc.charCodeAt(1) - 65);
}

// ---------- 1. 出口 IP 信息 ----------
function checkIP() {
return get("https://ipinfo.io/json", { policy: GROUP}).then(function (r) {
if (r.ok && r.status === 200) {
try {
var j = JSON.parse(r.body);
if (j.ip) {
var asn = "";
if (typeof $utils!== "undefined" && $utils.ipasn) {
var a = $utils.ipasn(j.ip);
if (a) asn = "AS" + a;
}
return {
ip: j.ip,
country: j.country || "",
text: j.city? (j.city + ", " + (j.region || "") + " " + (j.country || "")): (j.country || ""),
org: j.org || asn,
tz: j.timezone || ""
};
}
} catch (e) {}
}
// 备用源 ip-api
return get("http://ip-api.com/json/?lang=zh-CN&fields=status,query,country,countryCode,regionName,city,isp,as,timezone", { policy: GROUP}).then(function (r2) {
if (r2.ok) {
try {
var j2 = JSON.parse(r2.body);
if (j2.status === "success") return { ip: j2.query, country: j2.countryCode, text: (j2.city + ", " + j2.regionName + " " + j2.country), org: j2.as + " " + j2.isp, tz: j2.timezone};
} catch (e) {}
}
return { ip: "", country: "", text: "查询失败", org: "", tz: ""};
});
});
}

// ---------- 2b. 节点 IP 纯净度 ----------
// 主数据源 proxycheck.io（免 key）：risk 风险分、proxy/vpn 标记、IP 类型（Residential/Business/Hosting）
// 交叉验证 ip-api.com：proxy / hosting / mobile 标记
// 两路请求都显式走 GROUP（默认「节点选择」），和出口 IP 查询同一条路，
// 否则它们会按配置规则走 FINAL，改了 argument 后可能测到另一个出口的 IP。
// 纯净度评分是基于这两项的综合换算（见下方扣分），不是某个官方分数，明细会一并显示，方便自己判断
function testPurity(ip) {
  if (!ip) return Promise.resolve(["纯净度：❓ 无出口 IP，跳过"]);
  var pcUrl = "https://proxycheck.io/v2/" + ip + "?vpn=3&asn=1&risk=1";
  var iaUrl = "http://ip-api.com/json/" + ip + "?fields=status,proxy,hosting,mobile";
  return Promise.all([get(pcUrl, { policy: GROUP }), get(iaUrl, { policy: GROUP })]).then(function (rs) {
    var pc = null, ia = null;
    try { var j = JSON.parse(rs[0].body); if (j.status === "ok" && j[ip]) pc = j[ip]; } catch (e) {}
    try { var j2 = JSON.parse(rs[1].body); if (j2.status === "success") ia = j2; } catch (e) {}
    if (!pc && !ia) return ["纯净度：❓ 检测失败（数据源不可用）"];
    var lines = [];
    lines.push("检测 IP：" + ip);
    if (pc) {
      var score = 100 - (typeof pc.risk === "number" ? pc.risk : 0);
      var flags = [];
      if (pc.proxy === "yes") { score -= 30; flags.push("代理:是"); } else flags.push("代理:否");
      if (pc.vpn === "yes") { score -= 20; flags.push("VPN:是"); } else flags.push("VPN:否");
      var typeZh = { "Residential": "住宅", "Business": "商业", "Hosting": "机房", "Wireless": "移动", "Education": "教育", "Government": "政府", "Banking": "金融" }[pc.type] || pc.type || "-";
      if (pc.type === "Hosting") score -= 25;
      else if (pc.type === "Business") score -= 10;
      if (ia) {
        if (ia.hosting && pc.type !== "Hosting") score -= 15;
        if (ia.mobile) score += 5;
      }
      if (score > 100) score = 100; if (score < 0) score = 0;
      var grade = score >= 85 ? "🟢 很纯净" : score >= 70 ? "🟢 纯净" : score >= 50 ? "🟡 一般" : score >= 30 ? "🟠 风险较高" : "🔴 很脏";
      lines.push("纯净度：" + grade + "（" + score + " 分）");
      lines.push("类型：" + typeZh + "（" + (pc.type || "-") + "） · 风险分：" + (typeof pc.risk === "number" ? pc.risk : "-") + " · " + flags.join(" · "));
      if (pc.provider) lines.push("提供商：" + pc.provider);
    } else {
      // 只有 ip-api 时的粗略评估
      var s2 = 70;
      if (ia.proxy) s2 -= 40;
      if (ia.hosting) s2 -= 20;
      if (ia.mobile) s2 += 10;
      if (s2 > 100) s2 = 100; if (s2 < 0) s2 = 0;
      lines.push("纯净度：约 " + s2 + " 分（粗略评估，主数据源不可用）");
    }
    if (ia) lines.push("交叉验证(ip-api)：代理 " + (ia.proxy ? "是" : "否") + " · 机房 " + (ia.hosting ? "是" : "否") + " · 移动网络 " + (ia.mobile ? "是" : "否"));
    return lines;
  });
}

// ---------- 2. 本地网络 / 接口信息（$network，手册 scripting/api） ----------
function localInfo() {
var n = (typeof $network!== "undefined")? $network: {};
var lines = [];
var v4 = n.v4 || {}, v6 = n.v6 || {}, wifi = n.wifi || {};
var iface = v4.primaryInterface || v6.primaryInterface || "-";
var kind = wifi.ssid? ("Wi-Fi：" + wifi.ssid): (n["cellular-data"]? "蜂窝数据": "-");
lines.push("接口：" + iface + "（" + kind + "）");
if (wifi.bssid) lines.push("BSSID：" + wifi.bssid);
if (v4.primaryAddress) lines.push("IPv4：" + v4.primaryAddress + (v4.primaryRouter? " 网关：" + v4.primaryRouter: ""));
if (v6.primaryAddress) lines.push("IPv6：" + v6.primaryAddress);
if (n.dns && n.dns.length) lines.push("DNS：" + n.dns.join(", "));
var cell = n["cellular-data"];
if (cell && (cell.carrier || cell.radio)) lines.push("蜂窝：" + (cell.carrier || "") + (cell.radio? " " + cell.radio: ""));
var env = (typeof $environment!== "undefined")? $environment: {};
if (env.system) lines.push("系统：" + env.system + (env["device-model"]? " " + env["device-model"]: "") + (env["surge-version"]? " · Surge " + env["surge-version"]: ""));
return lines;
}

// ---------- 3. 当前策略 ----------
function currentPolicy() {
try {
var d = $surge.selectGroupDetails();
if (d && d.decisions && d.decisions[GROUP]) return GROUP + " → " + d.decisions[GROUP];
} catch (e) {}
return GROUP;
}

// ---------- 4. 流媒体检测 ----------
function testNetflix() {
// 双片源法：81280792 = 奈飞自制，70143836 = 非自制授权片
return Promise.all([
get("https://www.netflix.com/title/81280792"),
get("https://www.netflix.com/title/70143836")
]).then(function (rs) {
var a = rs[0], b = rs[1];
if (!a.ok &&!b.ok) return "❓ 检测失败（网络）";
if (a.status === 200 && b.status === 200) {
var loc = headerLoc(a.headers) || headerLoc(b.headers);
return "✅ 完整解锁" + (loc? " (" + loc + ")": "");
}
if (a.status === 200 && b.status === 404) return "⚠️ 仅自制剧";
if (a.status === 403 || b.status === 403) return "❌ 未解锁";
if (a.status === 404) return "❌ 未解锁";
return "❓ 无法判定 (" + a.status + "/" + b.status + ")";
});
}
function headerLoc(h) {
if (!h) return "";
var v = h["x-originating-url"] || h["Location"] || h["location"] || "";
var m = String(v).match(/\/([a-z]{2})(?:-[a-z]{2})?\//i);
return m? m[1].toUpperCase(): "";
}
function testDisney() {
return get("https://www.disneyplus.com/").then(function (r) {
if (!r.ok) return "❓ 检测失败（网络）";
var body = r.body.toLowerCase();
if (body.indexOf("not available in your region") >= 0 || body.indexOf("not available in your country") >= 0 || body.indexOf("unavailable in your region") >= 0) return "❌ 未解锁";
if (r.status === 200) return "✅ 已解锁";
if (r.status === 403) return "❌ 未解锁/被拦截";
return "❓ 无法判定 (" + r.status + ")";
});
}
function testYouTube() {
return get("https://www.youtube.com/premium").then(function (r) {
if (!r.ok) return "❓ 检测失败（网络）";
var body = r.body;
if (/premium is not available in your country/i.test(body) || /isn't available in your country/i.test(body) || /not available in your country/i.test(body)) return "❌ 未解锁";
var m = body.match(/"countryCode"\s*:\s*"([A-Z]{2})"/) || body.match(/contentRegion[^A-Z]{0,10}([A-Z]{2})/);
if (r.status === 200) return "✅ 已解锁" + (m? " (" + m[1] + ")": "");
return "❓ 无法判定 (" + r.status + ")";
});
}
function testTikTok() {
return get("https://www.tiktok.com/explore").then(function (r) {
if (!r.ok) return "❓ 检测失败（网络）";
var m = r.body.match(/"region"\s*:\s*"([A-Z]{2})"/i) || r.body.match(/store-region=([a-z]{2})/i);
if (r.status === 200 && m) return "✅ 已解锁 (" + m[1].toUpperCase() + ")";
if (r.status === 200) return "✅ 可访问";
if (r.status === 403) return "❌ 未解锁/被拦截";
return "❓ 无法判定 (" + r.status + ")";
});
}

// ---------- 5. AI 检测 ----------
function testChatGPT() {
return Promise.all([
get("https://api.openai.com/v1/models"),
get("https://chatgpt.com/cdn-cgi/trace")
]).then(function (rs) {
var api = rs[0], trace = rs[1];
var loc = "";
var m = trace.body.match(/loc=([A-Z]{2})/);
if (m) loc = m[1];
if (api.status === 401) return "✅ 已解锁" + (loc? " (" + loc + ")": ""); // 401=地区可用、只是没带 key
if (api.status === 403) return "❌ 未解锁" + (loc? " (" + loc + ")": "");
if (!api.ok && trace.ok && loc) return "❓ API检测失败，出口地区 " + loc;
return "❓ 无法判定 (" + api.status + ")";
});
}
function testClaude() {
return get("https://claude.ai/login").then(function (r) {
if (!r.ok) return "❓ 检测失败（网络）";
var body = r.body.toLowerCase();
if (body.indexOf("unavailable in your region") >= 0 || body.indexOf("app-unavailable-in-region") >= 0 || body.indexOf("not available in your region") >= 0) return "❌ 未解锁（地区限制）";
if (r.status === 200) return "✅ 已解锁";
// Claude 对脚本请求常直接回 403 的 Cloudflare 校验页，这不是地区封锁，不能误判
if (r.status === 403) return "❓ 无法判定（被 Cloudflare 拦截）";
return "❓ 无法判定 (" + r.status + ")";
});
}
function testGemini() {
return get("https://gemini.google.com/app").then(function (r) {
if (!r.ok) return "❓ 检测失败（网络）";
var body = r.body;
if (/isn't available in your country/i.test(body) || /not currently available in your country/i.test(body) || /not available in your country/i.test(body)) return "❌ 未解锁";
if (r.status === 200) return "✅ 已解锁";
return "❓ 无法判定 (" + r.status + ")";
});
}

// ---------- 主流程 ----------
(function () {
  var others = Promise.all([
    testNetflix(), testDisney(), testYouTube(), testTikTok(),
    testChatGPT(), testClaude(), testGemini()
  ]);
  var jobs = checkIP().then(function (ipInfo) {
    return Promise.all([others, testPurity(ipInfo.ip)]).then(function (x) {
      return [ipInfo].concat(x[0], [x[1]]);
    });
  });
  var timer = setTimeout(function () { finish(null, true); }, 25000);
  var doneOnce = false;
  function finish(rs, timeout) {
    if (doneOnce) return; doneOnce = true;
    clearTimeout(timer);
    var lines = [];
    if (timeout || !rs) {
      lines.push("检测超时，部分项目未完成，请点刷新重试。");
      lines = lines.concat(["", "-- 本地网络 / 接口 --"].concat(localInfo()));
      $done({ title: "🌐 网络信息与解锁检测", content: lines.join("\n"), icon: "network", "icon-color": "#F6A21E" });
      return;
    }
    var ip = rs[0];
    lines.push("-- 节点出口 IP --");
    if (ip.ip) {
      lines.push("IP：" + ip.ip + "  " + flag(ip.country) + " " + ip.text);
      if (ip.org) lines.push("ASN/运营商：" + ip.org);
      if (ip.tz) lines.push("时区：" + ip.tz);
    } else lines.push(ip.text);
    lines.push("当前策略：" + currentPolicy());
    lines.push("");
    lines.push("-- 节点 IP 纯净度 --");
    lines = lines.concat(rs[8] || ["纯净度：❓ 未检测"]);
    lines.push("");
    lines.push("-- 本地网络 / 接口 --");
    lines = lines.concat(localInfo());
    lines.push("");
    lines.push("-- 流媒体解锁 --");
    lines.push("Netflix：" + rs[1]);
    lines.push("Disney+：" + rs[2]);
    lines.push("YouTube Premium：" + rs[3]);
    lines.push("TikTok：" + rs[4]);
    lines.push("");
    lines.push("-- AI 解锁 --");
    lines.push("ChatGPT / OpenAI：" + rs[5]);
    lines.push("Claude：" + rs[6]);
    lines.push("Gemini：" + rs[7]);
    $done({ title: "🌐 网络信息与解锁检测", content: lines.join("\n"), icon: "network", "icon-color": "#3B82F6" });
  }
  jobs.then(function (rs) { finish(rs, false); }).catch(function (e) { finish(null, true); });
})();
