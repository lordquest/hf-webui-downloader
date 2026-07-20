# HF WebUI Downloader

> Author: **lordquest** — lordquest@163.com

跨平台的 Hugging Face 图形界面下载工具(WebUI)。输入仓库网页 URL 或 `owner/repo`,
自动列出可下载文件(可勾选),点击下载即可逐文件下载,带实时进度、取消、重试。

## 特性
- 解析 `https://huggingface.co/<owner>/<repo>/tree/<revision>` 或裸 `owner/repo`
- 列出仓库文件(文件名 + 大小),可勾选下载
- 默认下载目录可配置(留空 = 工具所在目录),持久化保存
- 按仓库隔离:`<默认目录>/<owner>-<repo>/` 下存放
- 逐文件下载,实时进度条 + 状态(等待/下载中/完成/已存在/失败/已取消)
- 单文件**取消** / **重试**
- **增量追加**:下载中可再提交新文件合并进同一任务
- **断点续传**:本地已存在且完整则跳过(状态 `已存在`)
- **镜像站**支持(设置 `HF_ENDPOINT`,如 `https://hf-mirror.com`)
- 底层用 `huggingface_hub` 自带的流式分块下载 + ETag/哈希完整性校验

## 运行
```bash
pip install -r requirements.txt
python app.py
# 浏览器打开 http://127.0.0.1:8000
```
或使用 uvicorn:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

## 结构
- `app.py` —— FastAPI 后端(解析 / 列举 / 设置 / 下载 / SSE 进度 / 取消 / 重试)
- `hf_ops.py` —— 核心:`parse_repo_input` / `list_files` / `build_target_dir` / `DownloadTask`
- `config.py` —— 默认下载目录与镜像地址持久化(`config.json`)
- `static/index.html` —— 纯静态前端(零前端框架)
- `requirements.txt`

## 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/parse` | 解析仓库输入 → repo_id/revision/subpath |
| POST | `/api/files` | 列举仓库文件 |
| GET/POST | `/api/settings` | 读写默认下载目录 / 镜像地址 |
| POST | `/api/download` | 启动或追加下载(传 `{path,size}` 列表) |
| GET | `/api/progress?task_id=` | SSE 实时进度推送 |
| POST | `/api/cancel` | 取消单个文件 |
| POST | `/api/retry` | 重试单个文件 |

## Author

- **lordquest**
- Email: lordquest@163.com
