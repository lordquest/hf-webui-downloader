## 1. 项目骨架与依赖
- [ ] 1.1 创建项目目录结构(`hf-downloader/`):`app.py`、`requirements.txt`、前端 `static/`、`config.json`(运行时生成)
- [ ] 1.2 编写 `requirements.txt`:`fastapi`、`uvicorn[standard]`、`huggingface_hub`(含 httpx)
- [ ] 1.3 编写 `config.py`:加载/保存 `config.json`(默认下载目录、镜像地址)

## 2. 后端核心逻辑
- [ ] 2.1 `hf_ops.py`:实现 `parse_repo_input(text)` —— 从 URL/裸 id 解析 repo_id / revision / subpath
- [ ] 2.2 `hf_ops.py`:实现 `list_files(repo_id, revision, subpath, endpoint)` —— 用 `HfApi.list_repo_tree` 枚举文件并返回 (path, size)
- [ ] 2.3 `hf_ops.py`:实现 `build_target_dir(repo_id, base_dir)` —— 生成 `<owner>-<repo>` 隔离目录
- [ ] 2.4 `hf_ops.py`:实现 `download_file(...)` —— 用 `hf_hub_download(local_dir=..., local_dir_use_symlinks=False)`,通过回调上报进度;支持取消标记
- [ ] 2.5 实现并发/任务管理:下载任务注册表,支持按文件取消、重试,进度状态内存维护

## 3. FastAPI 接口
- [ ] 3.1 `GET /` 返回前端首页
- [ ] 3.2 `POST /api/parse` 解析仓库输入
- [ ] 3.3 `POST /api/files` 列举仓库文件
- [ ] 3.4 `GET/POST /api/settings` 读写默认下载目录与镜像地址
- [ ] 3.5 `POST /api/download` 启动选中文件下载(返回任务 id)
- [ ] 3.6 `GET /api/progress?task_id=...` 以 SSE 推送进度(或轮询 JSON)
- [ ] 3.7 `POST /api/cancel` 取消单个文件; `POST /api/retry` 重试单个文件

## 4. 前端 WebUI
- [ ] 4.1 仓库输入框 + "解析/列举"按钮,展示可勾选文件列表(文件名 + 大小 + 全选)
- [ ] 4.2 设置面板:默认下载目录、镜像地址
- [ ] 4.3 下载控制:开始下载按钮、单文件进度条与状态、取消/重试按钮
- [ ] 4.4 通过 EventSource(SSE)实时刷新进度

## 5. 验证
- [ ] 5.1 本地启动 `python app.py`,浏览器打开,用示例 repo 验证解析/列举/下载/进度/隔离目录
- [ ] 5.2 验证未设默认目录时回落到工具所在目录
- [ ] 5.3 验证镜像地址生效(可临时设一个错误地址确认报错路径,或设 hf-mirror 验证列举)
