## 1. 修复设置回填
- [ ] 1.1 `config.load_config` 合并时保留 `download_dir_set` 标记
- [ ] 1.2 前端 `openSettings` 依据 `download_dir_set` 回填已保存目录,缺失时留空
- [ ] 1.3 本地验证:GET /api/settings 返回 download_dir_set;打开设置显示已保存目录
