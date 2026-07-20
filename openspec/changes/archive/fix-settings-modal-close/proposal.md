## Why
设置弹窗 `#settingsModal` 在 HTML 上写死了内联样式 `style="...display:flex;..."`。
`.hidden { display:none }` 是样式表层规则,无法覆盖内联 `display:flex`,导致调用
`classList.add("hidden")` 后弹窗实际不隐藏。表现:点"保存"后弹窗一直停留,遮挡下方下载 UI,
用户无法继续操作。

## What Changes
### 1. 改用 style.display 控制弹窗显隐
所有打开/关闭设置弹窗的地方改为直接设置 `$("settingsModal").style.display = "flex" / "none"`,
不再依赖 `.hidden` 类去覆盖内联 display。

### 2. 保存后即时关闭
"保存"成功后立即隐藏弹窗(去掉易误读的延时),并清空提示信息。
