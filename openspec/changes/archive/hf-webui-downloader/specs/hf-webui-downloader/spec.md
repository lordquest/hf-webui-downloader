## ADDED Requirements

### Requirement: 仓库标识解析
The system SHALL 从用户输入(可能是完整 HF 网页 URL 或裸 `owner/repo`)中解析出 `repo_id`(格式 `owner/repo`)、`revision`(默认 `main`)与可选的子路径 `subpath`。

#### Scenario: 解析完整网页 URL
- **WHEN** 用户输入 `https://huggingface.co/SC117/Agents-A1-Uncensored-MTP-APEX-GGUF/tree/main`
- **THEN** 系统解析出 repo_id=`SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`,revision=`main`,subpath=空

#### Scenario: 解析裸 repo_id
- **WHEN** 用户输入 `SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`
- **THEN** 系统解析出 repo_id=`SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`,revision=`main`

### Requirement: 仓库文件列举
The system SHALL 调用 `huggingface_hub` 的 `list_repo_tree`(或 `HfApi.list_repo_tree`)枚举指定 repo_id + revision + subpath 下的所有文件,返回文件名与大小,供前端以复选框列表展示。

#### Scenario: 列举成功
- **WHEN** 用户提交一个存在的公开 repo_id
- **THEN** 前端展示该仓库(含 subpath 范围内)所有文件的复选框列表,每行显示文件名与大小

#### Scenario: 列举失败
- **WHEN** repo_id 不存在或网络不可达
- **THEN** 系统向前端返回明确的错误信息(如 "仓库不存在 / 网络错误"),不展示空列表

### Requirement: 默认下载目录配置
The system SHALL 允许用户设置默认下载目录;未设置时默认使用工具所在目录。配置须持久化(本地 JSON 文件)。

#### Scenario: 用户显式设置目录
- **WHEN** 用户在设置中填入 `F:\download` 并保存
- **THEN** 后续下载默认落到 `F:\download`,且该设置重启后仍生效

#### Scenario: 未设置目录
- **WHEN** 用户从未设置默认下载目录
- **THEN** 系统使用工具自身所在目录作为默认下载目录

### Requirement: 按仓库隔离目录结构
The system SHALL 在默认下载目录下,为每次下载创建 `<owner>-<repo>` 子目录(将原 repo_id 中的 `/` 替换为 `-`),选中文件下载到该子目录内(保留仓库内相对路径)。

#### Scenario: 下载隔离
- **WHEN** 用户下载 `SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`
- **THEN** 系统在默认下载目录下创建 `SC117-Agents-A1-Uncensored-MTP-APEX-GGUF\`,文件存放于其内,而非直接散落于默认下载目录根

### Requirement: 逐文件下载与进度推送
The system SHALL 对每个选中文件调用 `hf_hub_download`(使用 `local_dir` 与 `local_dir_use_symlinks=False`),借助 `huggingface_hub` 自带的**分块流式下载与 ETag/哈希完整性校验**(失败时自动重试该文件),并通过进度接口(SSE 或轮询)向前端实时推送每个文件的下载状态(等待中 / 下载中 / 完成 / 失败 / 已取消 / 已存在)、进度百分比、已下载字节与总字节。下载任务 SHALL 支持在运行期间接收新的文件追加请求并合并进同一任务。

#### Scenario: 单文件进度可见
- **WHEN** 用户勾选若干文件并开始下载
- **THEN** 前端能实时看到每个文件的状态与进度百分比

#### Scenario: 单文件取消
- **WHEN** 用户对某个正在下载的文件点击"取消"
- **THEN** 该文件下载被中止,状态变为"已取消",其余文件不受影响继续下载

#### Scenario: 单文件重试
- **WHEN** 某个文件状态为"失败"或"已取消",用户点击"重试"
- **THEN** 系统重新对该文件执行下载

#### Scenario: 断点续传(本地已存在则跳过)
- **WHEN** 同一仓库文件此前已完整下载到目标目录,用户再次提交该文件下载
- **THEN** 系统检测到本地已存在且完整,状态标记为"已存在"并跳过实际下载,不重复占用带宽

#### Scenario: 增量追加下载
- **WHEN** 某次下载任务正在运行,用户再勾选若干新文件并提交"下载"
- **THEN** 新文件被合并进同一运行中的任务,与原有文件一起继续下载,前端进度列表实时增加对应条目

### Requirement: 镜像站地址支持
The system SHALL 允许用户在设置中配置镜像站地址(如 `https://hf-mirror.com`),配置后下载请求通过 `HF_ENDPOINT` 环境变量指向该镜像;未配置时使用官方默认 `https://huggingface.co`。

#### Scenario: 使用镜像
- **WHEN** 用户设置镜像地址为 `https://hf-mirror.com`
- **THEN** 后续列举与下载均通过该镜像地址进行

### Requirement: 跨平台 WebUI
The system SHALL 提供基于 FastAPI 的后端(REST + 进度推送)与纯静态 HTML/JS 前端,用户通过浏览器访问即可使用,无需为不同操作系统单独打包。

#### Scenario: 启动与使用
- **WHEN** 用户在任意支持 Python 的平台上运行 `python app.py`
- **THEN** 终端打印本地访问地址(如 `http://127.0.0.1:8000`),浏览器打开后即可使用全部功能
