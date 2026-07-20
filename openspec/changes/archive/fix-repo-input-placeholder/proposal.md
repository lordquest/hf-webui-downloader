## Why
仓库输入框的 `placeholder` 被填成了很长的真实风格网址
`https://huggingface.co/SC117/Agents-A1-Uncensored-MTP-APEX-GGUF/tree/main`。
在深色背景下该 placeholder 对比度极低,看起来像"已经填好的内容";而输入框实际为空。
此时用户点击"解析并列举",前端 `if (!input) return;` 会**静默返回、无任何提示**,
表现为"点了按钮什么也没发生",非常困惑。

## What Changes
### 1. placeholder 改为明显是提示的短示例
把 placeholder 换成简短、一眼能看出是占位提示的文本(如 `https://huggingface.co/owner/repo`),
避免与真实输入混淆。

### 2. 空输入点击解析给出明确提示
`btnList` 在输入为空时不再静默 return,而是显示错误提示"请先粘贴仓库网址或 repo_id",
让用户知道需要输入内容。
