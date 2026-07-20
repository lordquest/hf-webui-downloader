## 1. 修复切换语言卡死登录徽章
- [ ] 1.1 移除 #loginBadge 的 data-i18n,改由 setLoginBadge+T() 设定
- [ ] 1.2 applyLang 记录 lastLoginStatus,切换时重调 setLoginBadge 重译;dlTarget 有内容则重译
- [ ] 1.3 本地验证:zh/en 切换徽章不卡死、dlTarget 刷新
