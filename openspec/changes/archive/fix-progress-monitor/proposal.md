## Why
下载大文件时,网页进度条一直是 0,而 CLI 里 `hf_hub_download` 自带的 tqdm 在持续增长
(如 841M/26.1G)。

根因:`hf_hub_download(local_dir=...)` 在下载过程中**先把数据写到同目录下的临时文件
`<metadata_parent>/<hash>.<etag>.incomplete`**,下载完成后才 move 到最终 `filename`
(见 huggingface_hub `file_download.py:_hf_hub_download_to_local_dir` 与
`_local_folder.py:LocalDownloadFilePaths.incomplete_path`)。而本工具的进度监控线程读的是
最终 `file_path` 的大小,该文件在下载期间始终为 0,只有最后 move 才出现 → 网页进度恒为 0。

## What Changes
### 1. 监控临时 .incomplete 文件
`_worker` 的进度监控线程改为:在启动 `hf_hub_download` 前记录 `target_dir` 下已有的
`*.incomplete` 文件集合;监控循环中找到"新增的" `.incomplete` 文件(单文件任务即唯一一个),
以其当前大小作为 `downloaded` 上报。这样网页进度与 CLI 真实下载进度一致。

### 2. 完成后以最终文件大小收口
下载完成后(`hf_hub_download` 返回),以最终 `file_path` 大小作为 `downloaded`/`total` 收口,
避免末尾抖动。
