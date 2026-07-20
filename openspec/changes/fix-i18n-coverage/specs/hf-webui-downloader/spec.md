## ADDED Requirements

### Requirement: 英文模式无中文残留
The system SHALL 在英文界面下,所有可读文案均为英文,不得残留中文。除已覆盖的静态/前端提示外,至少须正确处理:① ETA 单位(`fmtEta` 的 时/分/秒 → h/m/s);② 进度区 "预计剩余" 前缀(zh=预计剩余,en=ETA);③ 运行时动态生成的进度行内 "取消"/"重试" 按钮(zh=取消/重试,en=Cancel/Retry)。这些文本 SHALL 经由 i18n 字典 `T()` 取词,确保切换语言后无中文残留。

#### Scenario: 英文模式 ETA 单位正确
- **WHEN** 英文界面下显示剩余时间
- **THEN** 显示为 "h/m/s" 而非 "时/分/秒"

#### Scenario: 英文模式无"预计剩余"中文
- **WHEN** 英文界面下总进度/单文件显示预估时间
- **THEN** 前缀为 "ETA" 而非 "预计剩余"

#### Scenario: 英文模式进度按钮为英文
- **WHEN** 英文界面下文件处于下载中/失败状态
- **THEN** 行内按钮显示 "Cancel"/"Retry" 而非 "取消"/"重试"
