## Why
部分仓库(gated / 受限 / 匿名限速)在没有 Hugging Face token 时下载很慢甚至被拒。
用户希望进入 WebUI 时检测本机是否已登录 HF(有无有效 token),未登录时引导用户
提供 token 完成本机登录,从而走已授权通道下载。当前本机已登录、有 token。

## What Changes

### 1. 进入页面静默检测 token 状态
后端在页面加载时通过 `huggingface_hub` 读取本机 token(环境变量 `HF_TOKEN` 或
`~/.cache/huggingface/token`),并调用 `whoami(token)` 网络校验其有效性,返回三种状态:
`logged_in`(有效) / `invalid`(有 token 文件但 whoami 失败) / `missing`(无 token)。
`config.json` 仅持久化"本机是否检测到 token"的状态标记(`hf_token_checked` / `hf_logged_in`),
**不存储 token 本身**。

### 2. 非阻断提示
前端进入页面即请求 token 状态。当状态为 `missing` 或 `invalid` 时,顶部显示一条
橙色非阻断提示条:"未检测到有效 HF token,受限仓库可能下载慢/被拒,点此查看如何登录",
并附"登录"入口;不阻挡正常下载操作。

### 3. WebUI 内粘贴 token 完成本机登录
提示条提供"登录"展开项:输入框粘贴 token + "登录"按钮。后端用 `huggingface_hub.login(token)`
(等价于非交互的 `huggingface-cli login`)将 token 持久化到本机默认位置,**不写入
`config.json`**。登录后重新 `whoami` 校验,成功则提示条消失、状态更新为 `logged_in`。

### 4. 链接引导
提示与登录区提供 https://huggingface.co/settings/tokens 链接,指导用户去创建 token。
