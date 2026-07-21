## ADDED Requirements

### Requirement: Linux 单文件可执行程序
The project SHALL 支持在 Linux 上打包为单文件可执行程序(`hf-downloader`,ELF 格式),
体验与 Windows exe 等价:命令行启动、自动打开默认浏览器、所有依赖内置。
构建通过 `build_linux.sh` 完成,内部调用 PyInstaller 执行 `hf_downloader.spec`。

#### Scenario: Linux 构建成功
- **WHEN** 在 Linux 环境执行 `./build_linux.sh`
- **THEN** 生成 `dist/hf-downloader` 单文件可执行程序

#### Scenario: Linux 运行并打开浏览器
- **WHEN** 执行 `./hf-downloader`(或 `./hf-downloader 8080`)
- **THEN** 后台启动 uvicorn 并延迟打开默认浏览器指向对应地址

#### Scenario: Linux 下 config 持久化路径正确
- **WHEN** 以 `./hf-downloader` 运行并在设置中修改下载目录
- **THEN** `config.json` 写入可执行文件所在目录(非临时目录),重启后生效
