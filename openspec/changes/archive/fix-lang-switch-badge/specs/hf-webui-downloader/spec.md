## ADDED Requirements

### Requirement: 切换语言不破坏动态状态文案
The system SHALL 在切换界面语言时,保留由运行时状态决定的动态文案的真实值,而非将其重置为静态占位词。具体而言:登录状态徽章(`#loginBadge`)的文案 SHALL 仅由 `setLoginBadge(status)` 依据真实登录状态(通过 `T()` 取词)设定,不得带 `data-i18n` 静态属性被 `applyLang()` 覆盖;切换语言后,若已检测过登录状态,徽章 SHALL 以新语言显示对应真实状态(已登录/未登录/失效),不得卡在"检测中"。此外,若已显示"下载到: …"目标目录,切换语言后 SHALL 以新语言重设该文案。

#### Scenario: 英文界面切换登录状态不卡死
- **WHEN** 页面已显示"已登录(HF token 有效)",用户切到 English 并保存
- **THEN** 徽章显示 "Logged in (HF token valid)",不出现 "Checking…"

#### Scenario: 中文界面切换登录状态不卡死
- **WHEN** 页面在 English 下显示 "Logged in (HF token valid)",用户切回中文并保存
- **THEN** 徽章显示 "已登录(HF token 有效)",不出现 "检测中…"

#### Scenario: 切换语言后目标目录文案刷新
- **WHEN** 已显示"下载到: F:\...",用户切换语言
- **THEN** 该文案以新语言重设(如 "Download to: F:\...")
