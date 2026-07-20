## 1. 中英双语切换
- [ ] 1.1 抽取全部静态文案 + 前端提示为 I18N {zh,en} 字典
- [ ] 1.2 后端 config.py 增加 language 字段;settings 接口读写
- [ ] 1.3 前端启动:config 有则用之,否则 navigator.language 判定并写回
- [ ] 1.4 设置弹窗加"语言"下拉;保存即重渲染(applyLang),立即生效
- [ ] 1.5 本地验证:zh/en 切换、系统语言默认、config 持久化
