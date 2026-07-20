## ADDED Requirements

### Requirement: 作者信息与 GitHub 可上传化
The system's repository SHALL 包含作者信息(`lordquest@163.com`,署名 lordquest),并处于可上传 GitHub 的状态:提供 `.gitignore` 忽略本地状态文件 `config.json` 与运行产物(`__pycache__/`、`*.pyc`、`*.incomplete`),提供 MIT `LICENSE`(版权人 lordquest,2026),`README.md` 含作者段,并完成 `git init` + 初次提交(仅纳入源码与文档,不含本地状态)。

#### Scenario: README 含作者信息
- **WHEN** 查看 README.md
- **THEN** 可见作者署名 lordquest 与邮箱 lordquest@163.com

#### Scenario: 本地状态不入库
- **WHEN** 执行初次 git 提交
- **THEN** `config.json`(含本机下载目录/登录标记)与 `__pycache__` 等被 `.gitignore` 忽略,不进入版本库

#### Scenario: 含 LICENSE
- **WHEN** 查看仓库根目录
- **THEN** 存在 MIT `LICENSE` 文件,版权人 lordquest,2026

#### Scenario: 可推送到 GitHub
- **WHEN** 本地已 init/commit 且用户已在 github.com 建好 Public 仓库
- **THEN** 通过 `git remote add origin <url>` + `git push -u origin main` 即可上传(README 提供步骤)
