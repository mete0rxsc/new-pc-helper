# Mete0r 新机装机助手

给刚拿到新电脑的用户准备的软件选择、异步下载、静默安装工具。

## 功能

- PySide6 / Qt Widgets 现代桌面 UI
- `QMainWindow` 主窗口、圆角卡片、大号自绘勾选框
- 按钮点击淡入动画、悬停状态、暗色现代样式
- 软件搜索、全选、清空
- 后台并发下载，不阻塞主界面
- 每个软件独立显示下载和安装进度
- `unzip: true` 的 ZIP 自动解压到桌面
- `install-command` 自动拼接到安装包后执行静默安装
- 支持外置 `app-list.json`，也内置一份默认列表用于单文件版本兜底

## 安装依赖

```powershell
pip install -r requirements.txt
```

## 运行

```powershell
python app.py
```

## app-list.json

程序启动时会优先读取 exe 或 `app.py` 同目录下的 `app-list.json`。如果用 PyInstaller `--add-data` 把 JSON 打进 exe，也能读取打包内的 JSON。前两者都不存在时，会自动使用 `app.py` 里的 `EMBEDDED_APP_LIST`。

单文件版本建议：

- 想固定列表：直接打包 `app.py`，使用内置列表。
- 想方便开源维护：把 `app-list.json` 放在 exe 同目录，程序会优先读取外置列表。

字段格式：

```json
{
  "name": "Steam",
  "URL": "https://example.com/installer.exe",
  "unzip": false,
  "install-command": "/S"
}
```

## 打包单文件

安装 PyInstaller：

```powershell
pip install pyinstaller
```

仅使用内置列表：

```powershell
pyinstaller --onefile --windowed --name Mete0rNewPcHelper app.py
```

如果希望把 `app-list.json` 也打进 exe：

```powershell
pyinstaller --onefile --windowed --name Mete0rNewPcHelper --add-data "app-list.json;." app.py
```

推荐开源发布时保留 `app-list.json`，方便别人提交 PR 更新软件下载地址。

## 开源地址

GitHub: https://github.com/mete0rxsc/new-pc-helper

©2026.Mete0r all right reserved.
