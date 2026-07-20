## Requirements

### Requirement: 仓库标识解析
The system SHALL 从用户输入(可能是完整 HF 网页 URL 或裸 `owner/repo`)中解析出 `repo_id`(格式 `owner/repo`)、`revision`(默认 `main`)与可选的子路径 `subpath`。输入框默认应为空;其占位提示 SHALL 为简短、明显是示例的文本,不得与真实输入混淆。当用户未输入任何内容即点击"解析并列举"时,系统 SHALL 显示明确提示而非静默无反应。

#### Scenario: 解析完整网页 URL
- **WHEN** 用户输入 `https://huggingface.co/SC117/Agents-A1-Uncensored-MTP-APEX-GGUF/tree/main`
- **THEN** 系统解析出 repo_id=`SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`,revision=`main`,subpath=空

#### Scenario: 解析裸 repo_id
- **WHEN** 用户输入 `SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`
- **THEN** 系统解析出 repo_id=`SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`,revision=`main`

#### Scenario: 空输入点击解析给出提示
- **WHEN** 用户未输入任何内容即点击"解析并列举"
- **THEN** 系统在仓库区域显示错误提示(如"请先粘贴仓库网址或 repo_id"),且不发起请求

### Requirement: 仓库文件列举
The system SHALL 调用 `huggingface_hub` 的 `list_repo_tree`(或 `HfApi.list_repo_tree`)枚举指定 repo_id + revision + subpath 下的所有文件,返回文件名与大小,供前端以复选框列表展示。

#### Scenario: 列举成功
- **WHEN** 用户提交一个存在的公开 repo_id
- **THEN** 前端展示该仓库(含 subpath 范围内)所有文件的复选框列表,每行显示文件名与大小

#### Scenario: 列举失败
- **WHEN** repo_id 不存在或网络不可达
- **THEN** 系统向前端返回明确的错误信息(如 "仓库不存在 / 网络错误"),不展示空列表

### Requirement: 默认下载目录配置
The system SHALL 允许用户设置默认下载目录;未设置时默认使用工具所在目录。配置须持久化(本地 JSON 文件)。再次打开设置页时,输入框 SHALL 回填当前已保存的默认下载目录,而非显示为空 / 占位符。设置弹窗在保存或取消后必须立即关闭,不得遮挡主界面的下载操作。

#### Scenario: 打开设置回填已保存目录
- **WHEN** 用户此前已保存默认下载目录为 `F:\AI\vllm_models`,再次点击"设置"打开弹窗
- **THEN** 目录输入框显示 `F:\AI\vllm_models`(已保存值),而非空白或占位符

#### Scenario: 用户显式设置目录
- **WHEN** 用户在设置中填入 `F:\download` 并保存
- **THEN** 后续下载默认落到 `F:\download`,且该设置重启后仍生效

#### Scenario: 未设置目录
- **WHEN** 用户从未设置默认下载目录
- **THEN** 系统使用工具自身所在目录作为默认下载目录,打开设置时输入框为空(显示占位符)

#### Scenario: 保存后弹窗关闭
- **WHEN** 用户在设置弹窗点击"保存"且请求成功
- **THEN** 弹窗立即隐藏,主界面(仓库输入、文件列表、下载按钮)恢复可操作

#### Scenario: 取消后弹窗关闭
- **WHEN** 用户在设置弹窗点击"取消"
- **THEN** 弹窗立即隐藏,主界面恢复可操作

### Requirement: 按仓库隔离目录结构
The system SHALL 在默认下载目录下,为每次下载创建 `<owner>-<repo>` 子目录(将原 repo_id 中的 `/` 替换为 `-`),选中文件下载到该子目录内(保留仓库内相对路径)。在用户列举完成、准备开始下载前,前端 SHALL 在"开始下载"按钮旁(或下方)预先显示本次将下载到的完整目标目录(默认下载目录 + `<owner>-<repo>`),格式如 `F:\AI\vllm_models\LeaderboardModel1-Agents-A1-AutoRound-W4A16-Tuning`,仅作展示、不提前创建目录。

#### Scenario: 下载隔离
- **WHEN** 用户下载 `SC117/Agents-A1-Uncensored-MTP-APEX-GGUF`
- **THEN** 系统在默认下载目录下创建 `SC117-Agents-A1-Uncensored-MTP-APEX-GGUF\`,文件存放于其内,而非直接散落于默认下载目录根

#### Scenario: 预先显示目标目录
- **WHEN** 用户解析 `LeaderboardModel1/Agents-A1-AutoRound-W4A16-Tuning`、默认保存目录为 `F:\AI\vllm_models`,列举完成
- **THEN** "开始下载"按钮旁/下显示 `F:\AI\vllm_models\LeaderboardModel1-Agents-A1-AutoRound-W4A16-Tuning`

### Requirement: 逐文件下载与进度推送
The system SHALL 对每个选中文件调用 `hf_hub_download`(使用 `local_dir`),借助 `huggingface_hub` 自带的**分块流式下载与 ETag/哈希完整性校验**(失败时自动重试该文件),并通过进度接口(SSE)向前端实时推送每个文件的下载状态(等待中 / 下载中 / 完成 / 失败 / 已取消 / 已存在)、进度百分比、已下载字节与总字节。进度百分比 SHALL 通过 `hf_hub_download` 的 `tqdm_class` 回调捕获真实字节进度(与 CLI 的 tqdm 同源)。除状态与进度条外,进度行 SHALL 展示**平均速度**与**预计剩余时间(ETA)**:前端基于文件开始下载的时间与已下载字节计算平均速度 = (当前已下 − 起始已下) / 已用秒数、ETA = (总量 − 当前已下) / 平均速度,并在下载进行中显示「已下 / 总量 · 平均速度 · 预计剩余 XXs」。下载任务 SHALL 支持在运行期间接收新的文件追加请求并合并进同一任务。进度面板中每个文件的文件名 SHALL 横向完整显示,状态徽章与取消/重试按钮位于文件名同行的右侧,进度条与「已下载 / 总量 · 速度 · 预计剩余」信息位于其下方一行。

#### Scenario: 单文件进度可见
- **WHEN** 用户勾选若干文件并开始下载
- **THEN** 前端能实时看到每个文件的状态与进度百分比,且进度随真实下载增长(非恒为 0)

#### Scenario: 大文件进度与 CLI 一致
- **WHEN** 下载一个 26GB 的大文件
- **THEN** 网页进度条从 0 持续增长到 100%,与 CLI 的 tqdm 进度基本同步,而非始终显示 0

#### Scenario: 显示平均速度与预计剩余时间
- **WHEN** 某文件正在下载且已知总量与已下载字节
- **THEN** 进度行显示形如 `5.4 GB / 24.3 GB · 12.3 MB/s · 预计剩余 25 分`(平均速度 + ETA),而非仅显示已下/总量

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

#### Scenario: 文件名不竖排
- **WHEN** 下载一个较长文件名的文件(如 Agents-A1-Uncensored-MTP-APEX-I-Balanced.gguf)
- **THEN** 进度面板中该文件名横向完整显示,绝不逐字符竖排

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

### Requirement: Hugging Face token 登录检测与引导
The system SHALL 在用户进入 WebUI 时静默检测本机 Hugging Face token 状态:读取本机 token(环境变量 `HF_TOKEN` 或 `~/.cache/huggingface/token`),并调用 `whoami(token)` 网络校验有效性,返回 `logged_in`(有效)/ `invalid`(有 token 但校验失败)/ `missing`(无 token) 三种状态。`config.json` SHALL 仅记录"本机是否检测到有效 token"的状态标记,**不得存储 token 本身**。当状态为 `missing` 或 `invalid` 时,前端 SHALL 显示一条橙色非阻断提示条(含创建 token 的官网链接与登录入口),不阻挡正常下载;当状态为 `logged_in` 时不显示提示。此外,前端 SHALL 在页面顶部常驻显示一个**登录状态徽章**:`logged_in` 显示绿色「已登录(HF token 有效)」,`invalid` 显示橙色「token 失效,请重新登录」,`missing` 显示橙色「未登录」;登录成功后徽章实时更新为已登录。

#### Scenario: 进入页面检测到已登录
- **WHEN** 本机存在有效 token(whoami 成功)
- **THEN** 不显示 token 提示条,下载正常进行

#### Scenario: 进入页面未检测到 token
- **WHEN** 本机无 token
- **THEN** 顶部显示橙色非阻断提示:"未检测到有效 HF token,受限仓库可能下载慢/被拒",并附官网创建链接与"登录"入口,下载操作不被阻挡

#### Scenario: 检测到失效 token
- **WHEN** 本机有 token 文件但 whoami 校验失败(如已吊销)
- **THEN** 同样显示橙色提示条,引导用户重新登录

#### Scenario: WebUI 内粘贴 token 完成本机登录
- **WHEN** 用户在提示条的登录区粘贴 token 并点击"登录"
- **THEN** 后端以非交互方式将 token 登录到本机默认位置(等价于 `huggingface-cli login`),**不写入 config.json**;登录后重新 whoami 校验,成功则提示条消失、状态更新为 `logged_in`

#### Scenario: config.json 不存储 token
- **WHEN** 系统持久化 token 检测状态
- **THEN** `config.json` 中仅含状态标记(如 `hf_logged_in`),不含任何 token 字符串

### Requirement: 总下载进度与完成态
The system SHALL 在开始下载后,于"开始下载"按钮**右侧同行**显示一个**总下载进度区**:一条总进度条(宽度 = ∑各文件已下载 / ∑各文件总量)与文字「已下总量 / 总量 · 预计剩余 XXs」(ETA 用整体平均速率估算:记录任务开始时刻与起始已下,平均总速 = (当前已下总量 − 起始已下) / 已用秒数,ETA = (总量 − 已下总量) / 平均总速)。当所有文件的 status 均为终态(`done` / `exists` / `failed` / `cancelled`)时,总进度区 SHALL 变为绿色「✓ 已完成」(进度条满 100%),常驻显示、不自动消失。该总进度区与"下载到: 目录"预览(按钮下方独立整行)互不干扰;无进行中下载任务时隐藏。

#### Scenario: 下载中显示总进度与 ETA
- **WHEN** 用户开始下载一批文件,部分仍在 downloading
- **THEN** "开始下载"按钮右侧显示总进度条与「已下总量 / 总量 · 预计剩余 XXs」,随真实下载增长

#### Scenario: 全部完成后显示已完成
- **WHEN** 该批所有文件均进入终态(done/exists/failed/cancelled)
- **THEN** 按钮右侧总进度区变为绿色「✓ 已完成」(进度条满 100%),常驻不消失

#### Scenario: 总进度区与目录预览互不干扰
- **WHEN** 列举完成且开始下载
- **THEN** "下载到: 目录"预览在按钮下方整行显示,总进度条在按钮右侧同行显示,二者均可见、不重叠

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

### Requirement: 界面中英双语切换
The system SHALL 支持界面在中文与英文之间切换。前端维护中/英双语文案字典,覆盖全部静态界面文案(标题、按钮、标签、设置项)与前端提示消息;后端原始异常消息保持原样。启动时:若 `config.json` 含 `language` 字段(zh/en)则使用该语言,否则前端依据系统显示语言(`navigator.language`,以 `zh` 开头视为中文、其余视为英文)判定并写回 `config.json`(仅记录、不改系统)。设置弹窗 SHALL 提供"语言"下拉(中文 / English),保存时写入 `config.json.language` 并**立即**以新语言重渲染整个界面,无需刷新页面。

#### Scenario: 配置指定语言
- **WHEN** `config.json` 中 `language` 为 `en`
- **THEN** 启动即以英文显示界面

#### Scenario: 无配置时跟随系统语言
- **WHEN** `config.json` 中无 `language`,且浏览器系统语言以 `zh` 开头
- **THEN** 启动以中文显示,并将 `language=zh` 写回 `config.json`

#### Scenario: 设置中切换语言立即生效
- **WHEN** 用户在设置中将语言从中文切换为 English 并保存
- **THEN** 界面立即变为英文,无需刷新;`config.json.language` 更新为 `en`

#### Scenario: 语言选项可回退
- **WHEN** 用户再次打开设置切回中文并保存
- **THEN** 界面立即变回中文,`config.json.language` 更新为 `zh`

### Requirement: 切换语言不破坏动态状态文案
The system SHALL 在切换界面语言时,保留由运行时状态决定的动态文案的真实值,而非将其重置为静态占位词。具体而言:登录状态徽章(`#loginBadge`)的文案 SHALL 仅由 `setLoginBadge(status)` 依据真实登录状态(通过 `T()` 取词)设定,不得带 `data-i18n` 静态属性被 `applyLang()` 覆盖;切换语言后,若已检测过登录状态,徽章 SHALL 以新语言显示对应真实状态(已登录/未登录/失效),不得卡在"检测中"。此外,若已显示"下载到: …"目标目录,切换语言后 SHALL 以新语言重设该文案。

#### Scenario: 英文界面切换登录状态不卡死
- **WHEN** 页面已显示"已登录(HF token 有效)",用户切到 English 并保存
- **THEN** 徽章显示 "Logged in (HF token valid)",不出现 "Checking…"

#### Scenario: 中文界面切换登录状态不卡死
- **WHEN** 页面在 English 下显示 "Logged in (HF token valid)",用户切回中文并保存
- **THEN** 徽章显示 "已登录(HF token 有效)",不出现 "检测中…"

#### Scenario: 切换语言后目标目录文案刷新
- **WHEN** 已显示"下载到: F:\...",用户切换语言
- **THEN** 该文案以新语言重设(如 "Download to: F:\...")
