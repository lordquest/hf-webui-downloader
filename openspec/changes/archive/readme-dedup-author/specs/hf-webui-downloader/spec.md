## ADDED Requirements

### Requirement: README 作者信息不重复
The `README.md` SHALL 仅在一处(底部 `## Author` 节)呈现作者信息(lordquest / lordquest@163.com),
标题下方不得重复 Author 引用;英文版链接(`> English version: [README.en.md]`)
可置于标题下方独立一行,不与作者信息重复。

#### Scenario: 顶部无重复 Author
- **WHEN** 查看 `README.md` 标题下方
- **THEN** 仅含英文版链接一行,不出现 `Author: lordquest` 引用

#### Scenario: 底部保留 Author
- **WHEN** 查看 `README.md` 末尾
- **THEN** 仍有 `## Author` 节含 lordquest / lordquest@163.com
