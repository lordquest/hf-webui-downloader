## Why
当前界面文案全部硬编码为中文,无法切换。需要支持中/英双语:设置里提供语言选项,启动时
按 `config.json` 的 `language` 字段显示;未配置时默认跟随系统显示语言(浏览器
`navigator.language`,`zh` 开头视为中文,否则英文)。切换语言立即生效,无需刷新。

## What Changes
### 1. 抽取文案为 i18n 字典
前端维护 `I18N = { zh: {...}, en: {...} }`,覆盖全部静态文案(标题、按钮、标签、
设置项)与前端提示消息(如"请先选择至少一个文件"、"列举失败"等)。后端原始异常消息
(如 huggingface 报错)保持原样。

### 2. 启动时按配置/系统语言初始化
启动时:`config.json` 有 `language`(zh/en)则用之;否则前端用 `navigator.language`
判定(`/^zh/i` → zh,否则 en),并把判定结果写回 `config.json`(仅记录,不改系统)。

### 3. 设置项 + 即时切换
设置弹窗新增"语言"下拉(中文/English),保存时写入 `config.json.language` 并**立即**
以新语言重渲染整个界面;未打开设置时也可即时切换(保存即生效,不刷新页面)。

### 4. 后端持久化
`config.py` 的 `config.json` 增加 `language` 字段(zh/en/None),`save_settings` 支持之;
`/api/settings` 返回与保存该字段。
