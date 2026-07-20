## MODIFIED Requirements

### Requirement: 按仓库隔离目录结构
The system SHALL 在默认下载目录下,为每次下载创建 `<owner>-<repo>` 子目录(将原 repo_id 中的 `/` 替换为 `-`),选中文件下载到该子目录内(保留仓库内相对路径)。在用户列举完成、准备开始下载前,前端 SHALL 在"开始下载"按钮旁(或下方)预先显示本次将下载到的完整目标目录(默认下载目录 + `<owner>-<repo>`),格式如 `F:\AI\vllm_models\LeaderboardModel1-Agents-A1-AutoRound-W4A16-Tuning`,仅作展示、不提前创建目录。

#### Scenario: 下载隔离
- **WHEN** 用户下载 `SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`
- **THEN** 系统在默认下载目录下创建 `SC117-Agents-A1-Uncensored-MTP-APEX-GGUF\`,文件存放于其内,而非直接散落于默认下载目录根

#### Scenario: 预先显示目标目录
- **WHEN** 用户解析 `LeaderboardModel1/Agents-A1-AutoRound-W4A16-Tuning`、默认保存目录为 `F:\AI\vllm_models`,列举完成
- **THEN** "开始下载"按钮旁/下显示 `F:\AI\vllm_models\LeaderboardModel1-Agents-A1-AutoRound-W4A16-Tuning`
