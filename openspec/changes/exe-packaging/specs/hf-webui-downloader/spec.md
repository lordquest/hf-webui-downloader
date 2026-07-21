## ADDED Requirements

### Requirement: 单文件 exe 打包
The project SHALL 支持打包为单文件 `hf-downloader.exe`,双击即可运行。打包使用
PyInstaller `--onefile` 模式,入口为新增 `launcher.py`,该脚本负责:
1. 在后台线程延迟 1.2s 后自动打开默认浏览器指向 `http://127.0.0.1:8000`
2. 在主线程启动 uvicorn(绑定 `127.0.0.1:8000`,加载 `app.app`)
3. 程序退出时清理 EventLoop

`config.py` 的 `CONFIG_PATH` SHALL 能正确识别 exe 运行环境:
- 源码模式:`CONFIG_PATH = <项目根>/config.json`(行为不变)
- exe 模式:`CONFIG_PATH = <exe所在目录>/config.json`(避免落在 `_MEIPASS` 临时目录)

打包配置通过 `hf_downloader.spec` 指定:
- `hiddenimports` 至少包含 `huggingface_hub` 全子模块(因该包内大量延迟导入,
  PyInstaller 静态分析难以全部捕获)
- `datas` 包含 `static/index.html`
- `excludes` 排除测试/开发用模块以减小体积

打包脚本 `build_exe.bat`(Windows)提供一键构建:
```bat
pip install pyinstaller
pyinstaller hf_downloader.spec
```
输出:`dist/hf-downloader.exe`(单文件)。

#### Scenario: 源码模式 config 路径不变
- **WHEN** 以 `python app.py` 运行
- **THEN** `config.json` 仍位于项目根目录,行为不变

#### Scenario: exe 模式 config 路径正确
- **WHEN** 以 `hf-downloader.exe` 运行
- **THEN** `config.json` 位于 exe 同一目录(非临时目录),设置可持久化

#### Scenario: 双击即打开浏览器
- **WHEN** 双击 `hf-downloader.exe`
- **THEN** 约 1.2s 后自动打开默认浏览器指向 `http://127.0.0.1:8000`,WebUI 可访问

#### Scenario: 单文件输出
- **WHEN** 执行 `build_exe.bat` 完成打包
- **THEN** `dist/hf-downloader.exe` 为单个可执行文件(无附属文件夹依赖)
