## Why

目前从 Hugging Face 下载模型 / 数据集只能使用 `hf` 命令行工具(`hf download <repo_id> --include "..." --local-dir .`),存在以下痛点:

1. 需要先手动到网页 `https://huggingface.co/<repo>` 找到 repo_id,再切到命令行敲命令。
2. 无法直观地勾选「只下载仓库里的某几个文件」。
3. 命令行没有图形化的进度 / 取消 / 重试体验。

本改动提供一个 **WebUI 图形界面下载工具**(跨平台,浏览器即可使用),用户输入 HF 仓库网页 URL(或 repo_id),工具自动解析 repo_id、列出仓库内可下载文件(带复选框),用户勾选后点击下载,后端逐文件下载并实时回传进度,且支持配置镜像站地址与默认下载目录。

## What Changes

### 1. 仓库 URL / repo_id 解析
输入 `https://huggingface.co/<owner>/<repo>/tree/main` 或裸 `owner/repo`,自动提取出 `repo_id`(`owner/repo`),并可识别 `tree/<revision>/<subpath>` 中的 revision 与子路径。

### 2. 文件清单列举
调用 `huggingface_hub.list_repo_tree`(或直接用 `HfApi`)枚举仓库文件,在 WebUI 中以带复选框的列表展示(文件名 + 大小)。

### 3. 默认下载目录配置
- 用户可设置默认下载目录(如 `F:\download`)。
- 未设置时,默认使用工具自身所在目录。
- 配置持久化保存(本地配置文件 / JSON)。

### 4. 按仓库隔离存放
下载 `owner/repo` 时,**先**在默认下载目录下建立 `<owner>-<repo>` 目录(把 `/` 替换为 `-`),文件放在该目录内,避免不同仓库文件混在一起。

### 5. 逐文件下载 + 进度 / 取消 / 重试
- 后端对每个选中文件调用 `hf_hub_download(local_dir=..., local_dir_use_symlinks=False)`。
- 通过 HTTP 长轮询 / SSE / WebSocket 将每个文件的下载进度(百分比、速度、已下/总量)实时推送给前端。
- 支持单个文件取消与重试;支持整批开始 / 暂停。
- 支持设置镜像地址(写 `HF_ENDPOINT` 环境变量,如 `https://hf-mirror.com`)。

### 6. 跨平台 WebUI
后端 FastAPI 提供 REST + 进度推送接口;前端为纯静态 HTML/JS(零前端框架),浏览器打开即用,天然跨平台。
