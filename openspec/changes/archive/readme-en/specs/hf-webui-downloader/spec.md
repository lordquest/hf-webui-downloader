## ADDED Requirements

### Requirement: 英文版 README
The repository SHALL 提供英文版 `README.en.md`,内容与中文 `README.md` 一一对应(简介、Features、Run、Structure、API 表、Author),代码块/命令/接口路径保持原样;并在 `README.md` 顶部添加指向 `README.en.md` 的英文版链接,方便不同语言用户阅读。

#### Scenario: 英文版存在且对齐
- **WHEN** 查看仓库根目录
- **THEN** 存在 `README.en.md`,含 Features/Run/Structure/API/Author 各节,与中文版内容对应

#### Scenario: 中文版可跳转英文版
- **WHEN** 查看 `README.md` 开头
- **THEN** 有指向 `README.en.md` 的链接
