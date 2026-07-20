## MODIFIED Requirements

### Requirement: Hugging Face token 登录检测与引导
The system SHALL 在用户进入 WebUI 时静默检测本机 Hugging Face token 状态:读取本机 token(环境变量 `HF_TOKEN` 或 `~/.cache/huggingface/token`),并调用 `whoami(token)` 网络校验有效性,返回 `logged_in`(有效)/ `invalid`(有 token 但校验失败)/ `missing`(无 token) 三种状态。`config.json` SHALL 仅记录"本机是否检测到有效 token"的状态标记,**不得存储 token 本身**。当状态为 `missing` 或 `invalid` 时,前端 SHALL 显示一条橙色非阻断提示条(含创建 token 的官网链接与登录入口),不阻挡正常下载;当状态为 `logged_in` 时不显示提示。此外,前端 SHALL 在页面顶部常驻显示一个**登录状态徽章**:`logged_in` 显示绿色「已登录(HF token 有效)」,`invalid` 显示橙色「token 失效,请重新登录」,`missing` 显示橙色「未登录」;登录成功后徽章实时更新为已登录。

#### Scenario: 进入页面检测到已登录
- **WHEN** 本机存在有效 token(whoami 成功)
- **THEN** 不显示 token 提示条,顶部徽章显示绿色「已登录(HF token 有效)」,下载正常进行

#### Scenario: 进入页面未检测到 token
- **WHEN** 本机无 token
- **THEN** 顶部显示橙色非阻断提示:"未检测到有效 HF token,受限仓库可能下载慢/被拒",并附官网创建链接与"登录"入口;顶部徽章显示橙色「未登录」,下载操作不被阻挡

#### Scenario: 检测到失效 token
- **WHEN** 本机有 token 文件但 whoami 校验失败(如已吊销)
- **THEN** 同样显示橙色提示条,徽章显示橙色「token 失效,请重新登录」

#### Scenario: WebUI 内粘贴 token 完成本机登录
- **WHEN** 用户在提示条的登录区粘贴 token 并点击"登录"
- **THEN** 后端以非交互方式将 token 登录到本机默认位置(等价于 `huggingface-cli login`),**不写入 config.json**;登录后重新 whoami 校验,成功则提示条消失、徽章更新为绿色「已登录(HF token 有效)」

#### Scenario: config.json 不存储 token
- **WHEN** 系统持久化 token 检测状态
- **THEN** `config.json` 中仅含状态标记(如 `hf_logged_in`),不含任何 token 字符串
