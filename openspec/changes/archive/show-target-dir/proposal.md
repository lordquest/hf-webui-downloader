## Why
列举完成、准备点"开始下载"时,用户看不到文件将落到哪个具体目录,只能在下载后才从
进度面板得知。希望在"开始下载"按钮旁/下**预先显示本次目标目录**(默认目录 + `<owner>-<repo>`),
如解析 `LeaderboardModel1/Agents-A1-AutoRound-W4A16-Tuning`、默认目录 `F:\AI\vllm_models`
时显示 `F:\AI\vllm_models\LeaderboardModel1-Agents-A1-AutoRound-W4A16-Tuning`。

## What Changes
### 1. 后端提供目标目录计算
新增 `hf_ops.target_dir_for(repo_id, base_dir)`(纯计算,不创建目录);`build_target_dir` 复用之。
新增 `GET /api/target_dir?repo_id=...`,基于当前 `config.json` 的 `download_dir` 返回
`target_dir` 字符串。

### 2. 前端列举后显示目标目录
"开始下载"按钮旁/下显示一行目标目录(带"下载到:"前缀,可换行,小字 muted)。
在列举成功并设置好仓库后请求 `/api/target_dir` 并渲染;切换仓库/重新列举时刷新。
仅展示,不提前创建目录(目录仍在实际下载时由 `build_target_dir` 创建)。
