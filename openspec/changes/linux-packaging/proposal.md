## Why
项目已有 Windows 单文件 exe 打包方案,但 Linux 用户无法使用 `.exe`。需要为 Linux
提供等价的单文件可执行程序构建方式,保持"双击/命令行启动 + 自动开浏览器"的
同等体验。

## What Changes
### 1. Linux 构建脚本
新增 `build_linux.sh`,在 Linux 环境下执行:
```bash
chmod +x build_linux.sh
./build_linux.sh
```
脚本自动安装 PyInstaller(若缺失)并执行 `pyinstaller hf_downloader.spec`,
输出 `dist/hf-downloader`(Linux ELF 可执行文件,无后缀)。

### 2. 跨平台 spec 调整
现有 `hf_downloader.spec` 已是跨平台 Python 代码,但在 Windows 上 `upx=True`
在 Linux 上也可能工作。为减少差异,spec 保持不变,仅通过 `build_linux.sh`
在 Linux 上调用。`launcher.py` 本身已跨平台(用 `webbrowser.open` + `sys.argv`
解析端口)。

### 3. 使用方式
Linux 用户拿到 `hf-downloader` 单文件后:
```bash
./hf-downloader            # 默认 8000 端口
./hf-downloader 8080       # 指定端口
```
启动后自动打开默认浏览器指向 `http://127.0.0.1:8000`(或指定端口)。

### 4. 限制说明
当前开发环境为 Windows,本次仅提供 Linux 构建脚本与说明,不实际在 Linux
上编译验证。用户在 Linux 机器上执行 `build_linux.sh` 即可生成。
