## 1. 修复进度监控读取错误的文件
- [ ] 1.1 `_worker` 监控线程改为追踪 `target_dir` 下新增的 `*.incomplete` 临时文件大小
- [ ] 1.2 下载完成后以最终 `file_path` 大小收口 downloaded/total
- [ ] 1.3 本地启动验证:下载大文件时网页进度从 0 持续增长(与 CLI 同步),非恒为 0
