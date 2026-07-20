## ADDED Requirements

### Requirement: 启动依赖检查与提示
The system SHALL 在后端启动时检查下载功能所依赖的关键第三方库是否齐备(至少包括 `fastapi`、`uvicorn`、`huggingface_hub`、`tqdm`),并通过健康检查接口(如 `GET /api/health`)返回缺失依赖列表与建议安装命令(`pip install -r requirements.txt`)。后端即使缺失依赖也 SHALL 正常启动(页面可打开、不硬性崩溃),仅作提示。前端进入页面时 SHALL 静默请求该健康检查;若存在缺失依赖,顶部显示一条**红色非阻断提示条**,列出缺失包名与安装命令,引导用户安装后重启,避免"点击下载才发现无法下载"。

#### Scenario: 依赖齐全
- **WHEN** 运行环境已安装全部关键依赖
- **THEN** 健康检查报告无缺失,前端不显示依赖提示条

#### Scenario: 缺失关键依赖
- **WHEN** 运行环境缺少 `huggingface_hub`(或 `fastapi`/`uvicorn`/`tqdm`)
- **THEN** 健康检查返回缺失列表;前端顶部显示红色提示条,列出缺失包名与 `pip install -r requirements.txt`;后端仍正常启动、页面可打开

#### Scenario: 安装命令可见
- **WHEN** 提示条显示
- **THEN** 提示含可复制的安装命令 `pip install -r requirements.txt`(或针对缺失包的 `pip install <pkg>`)
