## 1. 后端 token 检测与登录
- [ ] 1.1 `hf_ops` / 新模块:实现 `check_hf_token()` —— 读本机 token + `whoami` 校验,返回 logged_in/invalid/missing
- [ ] 1.2 `config.py`:`config.json` 仅记录 `hf_logged_in` 状态标记,不存 token
- [ ] 1.3 `app.py`:`GET /api/token` 返回状态;`POST /api/token/login` 用 `login(token)` 本机登录后重新校验

## 2. 前端提示与登录区
- [ ] 2.1 进入页面静默请求 `/api/token`,missing/invalid 时显示橙色非阻断提示条(含官网链接)
- [ ] 2.2 提示条"登录"展开:token 输入框 + 登录按钮,成功后提示消失、状态刷新
- [ ] 2.3 本地验证:本机已登录→无提示;临时改状态→出现提示;粘贴 token→登录成功消失
