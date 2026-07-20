## Why
用户在设置页保存了默认下载目录(如 `F:\AI\vllm_models`),`config.json` 中也正确写入了
`download_dir` 与 `download_dir_set: true`。但再次打开设置页时,目录输入框却显示占位符
`例如 F:\download`(即空白),没有回填已保存的值。

根因:`config.load_config()` 在合并配置时只保留 `_DEFAULTS` 内的键(`download_dir`、
`endpoint`),把 `download_dir_set` 过滤掉了。于是 `GET /api/settings` 的响应里没有
`download_dir_set` 字段,前端 `openSettings` 判断 `s.download_dir_set` 为 undefined(假值),
便把输入框置空、只显示占位符。

## What Changes
### 1. config.load_config 保留 download_dir_set
合并时同时保留 `download_dir_set` 标记,使 `GET /api/settings` 能返回它。

### 2. 前端打开设置时回填已保存目录
`openSettings` 中:若 `download_dir_set` 为真且 `download_dir` 非空,则把该值填入输入框;
否则留空(占位符提示)。不再因标记缺失而误清空。
