## Why
项目已基本完成,需作为新项目上传 GitHub。需要:① 在 README/项目元信息中加入作者信息
(lordquest@163.com);② 让仓库处于"可上传"状态 —— 忽略本地状态文件 `config.json`(含本机
下载目录/登录标记,不应入库),补充 `LICENSE`(MIT)、`.gitignore`,并 `git init` + 初次提交。
GitHub 仓库由用户在 github.com 创建(Public),本机无 `gh` CLI,故本地完成 init/commit 后
给出 push 步骤。

## What Changes
### 1. 作者信息
- `README.md` 顶部/末尾增加作者段:`Author: lordquest — lordquest@163.com`。
- 可选:项目标题下加一行作者署名。

### 2. 仓库可上传化
- 新增 `.gitignore`:忽略 `config.json`、`__pycache__/`、`*.pyc`、`*.incomplete`(hf 临时文件)、
  本地运行产物。源码(`app.py`/`hf_ops.py`/`config.py`/`static/`/`requirements.txt`/`README.md`/
  `openspec/`)纳入版本控制。
- 新增 `LICENSE`(MIT,版权人 lordquest,2026)。
- `git init` + 初次提交(仅源码与文档,不含 `config.json` 等本地状态)。

### 3. 上传步骤(用户侧)
- 用户在 github.com 新建 Public 仓库(如 `hf-webui-downloader`),本地 `git remote add origin`
  后 `git push -u origin main`(给出命令)。
