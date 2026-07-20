## ADDED Requirements

### Requirement: 界面中英双语切换
The system SHALL 支持界面在中文与英文之间切换。前端维护中/英双语文案字典,覆盖全部静态界面文案(标题、按钮、标签、设置项)与前端提示消息;后端原始异常消息保持原样。启动时:若 `config.json` 含 `language` 字段(zh/en)则使用该语言,否则前端依据系统显示语言(`navigator.language`,以 `zh` 开头视为中文、其余视为英文)判定并写回 `config.json`(仅记录、不改系统)。设置弹窗 SHALL 提供"语言"下拉(中文 / English),保存时写入 `config.json.language` 并**立即**以新语言重渲染整个界面,无需刷新页面。

#### Scenario: 配置指定语言
- **WHEN** `config.json` 中 `language` 为 `en`
- **THEN** 启动即以英文显示界面

#### Scenario: 无配置时跟随系统语言
- **WHEN** `config.json` 中无 `language`,且浏览器系统语言以 `zh` 开头
- **THEN** 启动以中文显示,并将 `language=zh` 写回 `config.json`

#### Scenario: 设置中切换语言立即生效
- **WHEN** 用户在设置中将语言从中文切换为 English 并保存
- **THEN** 界面立即变为英文,无需刷新;`config.json.language` 更新为 `en`

#### Scenario: 语言选项可回退
- **WHEN** 用户再次打开设置切回中文并保存
- **THEN** 界面立即变回中文,`config.json.language` 更新为 `zh`
