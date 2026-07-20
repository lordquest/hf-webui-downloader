## MODIFIED Requirements

### Requirement: 仓库标识解析
The system SHALL 从用户输入(可能是完整 HF 网页 URL 或裸 `owner/repo`)中解析出 `repo_id`(格式 `owner/repo`)、`revision`(默认 `main`)与可选的子路径 `subpath`。输入框默认应为空;其占位提示 SHALL 为简短、明显是示例的文本,不得与真实输入混淆。当用户未输入任何内容即点击"解析并列举"时,系统 SHALL 显示明确提示而非静默无反应。

#### Scenario: 解析完整网页 URL
- **WHEN** 用户输入 `https://huggingface.co/SC117/Agents-A1-Uncensored-MTP-APEX-GGUF/tree/main`
- **THEN** 系统解析出 repo_id=`SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`,revision=`main`,subpath=空

#### Scenario: 解析裸 repo_id
- **WHEN** 用户输入 `SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`
- **THEN** 系统解析出 repo_id=`SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`,revision=`main`

#### Scenario: 空输入点击解析给出提示
- **WHEN** 用户未输入任何内容即点击"解析并列举"
- **THEN** 系统在仓库区域显示错误提示(如"请先粘贴仓库网址或 repo_id"),且不发起请求
