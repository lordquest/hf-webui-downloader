## 1. 启动依赖检查与前端提示
- [ ] 1.1 后端:启动时探测 fastapi/uvicorn/huggingface_hub/tqdm,`GET /api/health` 返回缺失列表+安装命令;导入 hf_ops 失败时兜底不崩
- [ ] 1.2 前端:进入页面静默查 /api/health,缺失时显示红色提示条(包名+安装命令)
- [ ] 1.3 本地验证:依赖齐全无提示;临时改名模拟缺失→出现红色提示
