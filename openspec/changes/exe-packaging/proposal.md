## Why
项目当前以源码方式运行,需安装 Python 环境并手动 `uvicorn app:app` 启动。为方便非技术用户使用,应打包为单文件 exe —— 双击即运行、自动打开浏览器、所有依赖内置。

## What Changes
### 1. 更新 `config.py` 的 `CONFIG_PATH` 以支持 exe 模式
`CONFIG_PATH` 在源码模式下不变(`<项目根>/config.json`);exe 模式下指向
`<exe所在目录>/config.json`(通过 `sys.frozen` / `sys.executable` 判定)。

### 2. 新增 `launcher.py`(打包入口)
- 后台线程延迟 1.2s 后 `webbrowser.open("http://127.0.0.1:8000")`
- 主线程 `uvicorn.run(app.app, host="127.0.0.1", port=8000, log_level="warning")`
- 支持 `--port` 命令行参数(可选,默认 8000)

### 3. 新增 `hf_downloader.spec`(PyInstaller 配置)
- 入口:`launcher.py`
- `hiddenimports`:`huggingface_hub` 及其常用子模块
- `datas`:[(`static/index.html`, `static`)]
- `excludes`:测试/开发模块以减小体积
- `onefile=True`, 输出 `hf-downloader.exe`

### 4. 新增 `build_exe.bat`(一键构建脚本)
- 安装 pyinstaller → 执行 `pyinstaller hf_downloader.spec`
- 输出:`dist/hf-downloader.exe`
