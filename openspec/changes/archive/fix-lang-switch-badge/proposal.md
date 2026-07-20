## Why
静态 `[data-i18n]` 元素由 `applyLang()` 整体重渲染。但登录状态徽章(`#loginBadge`)
是**动态**元素:其文案由 `setLoginBadge(status)` 依真实登录状态设定,却带了
`data-i18n="badge.detecting"`。切换语言时 `applyLang()` 会把它覆盖成静态
"Checking…"(或其它语言对应词),且不会回写当前真实状态,于是出现"已登录却显示 Checking…"的卡死现象。
同理,"下载到: …"(`#dlTarget`)也是动态 T() 文案,切换语言后也不会刷新。

## What Changes
### 1. 徽章改回纯动态(去掉 data-i18n)
`#loginBadge` 移除 `data-i18n` 属性,完全由 `setLoginBadge(status)` 用 `T()` 设定文案;
`applyLang()` 不再触碰它。这样切换语言时徽章保留真实状态文案(若已检测过则仍是已登录/未登录)。

### 2. applyLang 刷新其余动态文本
`applyLang()` 末尾补充:若已检测过登录状态(`lastLoginStatus` 记录),则重调
`setLoginBadge(lastLoginStatus)` 以便重新翻译;若已显示目标目录(`#dlTarget` 有内容),
按当前语言重设 "下载到: …" 文案。

### 3. 启动顺序保证
`onload` 先 `applyLang()`(设初始静态文案 + 初始"检测中"),再 `checkToken()`(异步检测后用
`setLoginBadge` 覆盖为真实状态);切换语言时不会覆盖真实状态。
