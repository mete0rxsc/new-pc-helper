import ctypes
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QObject, QRunnable, QThreadPool, QTimer, Qt, Signal, Slot, QPropertyAnimation, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QComboBox,
)

APP_TITLE = "新机装机助手"
GITHUB_URL = "https://github.com/mete0rxsc/new-pc-helper"
COPYRIGHT = "©2026.Mete0r all right reserved."
MAX_WORKERS = 3

EMBEDDED_APP_LIST = [
    {
        "name": "Steam",
        "URL": "https://media.st.dl.eccdnx.com/client/installer/SteamSetup.exe",
        "unzip": False,
        "install-command": "/S /NCRC",
    },
    {
        "name": "Epic Games Launcher",
        "URL": "https://epicgames-download1.akamaized.net/Builds/UnrealEngineLauncher/Installers/Windows/EpicInstaller-20.1.0.exe?launcherfilename=EpicInstaller-20.1.0.exe",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "WeChat",
        "URL": "https://dldir1.qq.com/weixin/Universal/Windows/WeChatWin_4.1.10.exe",
        "unzip": False,
        "install-command": "/S /NCRC",
    },
    {
        "name": "Oopz",
        "URL": "https://downloadcdn.oopz.cn/release/141/oopz_setup_v1.4.1.1.exe",
        "unzip": False,
        "install-command": "/S /NCRC",
    },
    {
        "name": "ToDesk",
        "URL": "https://dl.todesk.com/irrigation/ToDesk_4.9.7.1.exe",
        "unzip": False,
        "install-command": "/S /NCRC",
    },
    {
        "name": "Kook",
        "URL": "https://dl.kookapp.cn/assets/release/html_pc/kook_2779/Kook_PC_Setup_v0.107.1.0_b2ZmaWNpYWwuc2l0ZS4uLi5wYw==.exe?auth_key=1781539821-e065ce4ab2fa51b70134c39c36f41789-10h3n8uz0-24f87bc2fcdbf543d29225db2169aa75",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "GeekUninstaller",
        "URL": "https://geekuninstaller.com/geek.zip",
        "unzip": True,
    },
    {
        "name": "7-Zip",
        "URL": "https://v4.gh-proxy.org/https://github.com/ip7z/7zip/releases/download/26.01/7z2601-x64.exe",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "图吧工具箱",
        "URL": "https://apac.tualatin.club/%E5%9B%BE%E5%90%A7%E5%B7%A5%E5%85%B7%E7%AE%B1202601.1%E5%AE%89%E8%A3%85%E5%8C%85.exe",
        "unzip": False,
        "install-command": "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART",
    },
    {
        "name": "QQ音乐",
        "URL": "https://dldir.y.qq.com/ecosfile/music_clntupate/pc/other/QQMusic_Setup_2228.exe?sign=1781539964-61v9Oqgv0rsi5oUj-0-ae50a6579abd3cfe95b41f7c127da61a",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "网易云音乐",
        "URL": "https://d8.music.126.net/dmusic2/NeteaseCloudMusic_Music_official_3.1.35.205293_64.exe",
        "unzip": False,
        "install-command": "/S /NCRC",
    },
    {
        "name": "Battle.net",
        "URL": "https://downloader.battlenet.com.cn/download/installer/win/1.0.66/Battle.net-Setup-CN.exe",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "SteamTools",
        "URL": "https://v4.gh-proxy.org/https://github.com/BeyondDimension/SteamTools/releases/download/3.1.0/Steam++_v3.1.0_win_x64.exe",
        "unzip": False,
        "install-command": "/S /NCRC",
    },
    {
        "name": "UU加速器",
        "URL": "https://uu.gdl.netease.com/5223/UU-6.9.2.exe?key1=32ff19b0a85e8a7346e7073cbbfee28d&key2=6a30cda1",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "QQ",
        "URL": "https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/092069d7/QQ_9.9.31_260528_x64_01.exe",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "火绒安全",
        "phpURL": "https://www.huorong.cn/product/versionShow60.php",
        "unzip": False,
        "install-command": "MANUAL_INSTALL_REQUIRED",
        "note": "不支持静默安装，下载后请手动安装"
    },
    {
        "name": "Google Chrome",
        "URL": "https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B60D513C6-17C4-7970-CFCC-6C7C545D8296%7D%26lang%3Dzh-CN%26browser%3D4%26usagestats%3D1%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3D-arch_x64-statsdef_1%26installdataindex%3Dempty/update2/installers/ChromeSetup.exe",
        "unzip": False,
        "install-command": "/S",
    },
    {
        "name": "游戏加加",
        "URL": "https://dl.gamepp.com/global/GamePP_International.exe",
        "unzip": False,
        "install-command": "/S"
    },
    {
        "name": "OBS Studio",
        "URL": "https://cdn-fastly.obsproject.com/downloads/OBS-Studio-32.1.2-Windows-x64-Installer.exe",
        "unzip": False,
        "install-command": "/S /NCRC"
    },
    {
        "name": "Java21(建议搭配MC食用)",
        "URL": "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.msi",
        "unzip": False,
        "install-command": "/qn /norestart"
    },
    {
        "name": "PCL2-CE",
        "URL": "https://v4.gh-proxy.org/https://github.com/PCL-Community/PCL-CE/releases/download/v2.14.6/PCL2_CE_Release_x64.exe",
        "unzip": False,
        "install-command": "",
        "portable": True,
        "note": "绿色单文件，自动部署并创建快捷方式"
    },
]


@dataclass
class AppItem:
    name: str
    url: str
    unzip: bool
    install_command: str = ""
    note: str = ""
    portable: bool = False


class AnimatedButton(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.effect = QGraphicsOpacityEffect(self)
        self.effect.setOpacity(1)
        self.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity", self)
        self.animation.setDuration(160)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def mousePressEvent(self, event) -> None:
        self.animate_to(0.68)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.animate_to(1)
        super().mouseReleaseEvent(event)

    def animate_to(self, value: float) -> None:
        self.animation.stop()
        self.animation.setStartValue(self.effect.opacity())
        self.animation.setEndValue(value)
        self.animation.start()


class ModernCheckBox(QCheckBox):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(36)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        box_size = 28
        box_x = 0
        box_y = (self.height() - box_size) // 2
        radius = 9

        if self.isChecked():
            painter.setBrush(QColor("#48d7ad"))
            painter.setPen(QPen(QColor("#48d7ad"), 2))
        else:
            painter.setBrush(QColor("#111722"))
            painter.setPen(QPen(QColor("#526078"), 2))
        painter.drawRoundedRect(box_x + 1, box_y + 1,
                                box_size - 2, box_size - 2, radius, radius)

        if self.isChecked():
            painter.setPen(QPen(QColor("#07110d"), 3,
                           Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(box_x + 8, box_y + 15, box_x + 13, box_y + 20)
            painter.drawLine(box_x + 13, box_y + 20, box_x + 21, box_y + 9)

        painter.setPen(QColor("#f8fafc"))
        painter.setFont(QFont("Microsoft YaHei UI", 11, QFont.Bold))
        painter.drawText(box_size + 14, 0, self.width() - box_size -
                         14, self.height(), Qt.AlignVCenter, self.text())


class WorkerSignals(QObject):
    status = Signal(str, int, str)
    done = Signal(str, int, str)
    error = Signal(str, int, str)


class InstallWorker(QRunnable):
    def __init__(self, app: AppItem, target_drive: str = "") -> None:
        super().__init__()
        self.app = app
        self.target_drive = target_drive
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            self.signals.status.emit(self.app.name, 2, "连接下载地址")

            # 1. 特殊处理：需要手动安装的软件（如火绒）
            if self.app.install_command == "MANUAL_INSTALL_REQUIRED":
                self.signals.status.emit(self.app.name, 10, "正在下载安装包")
                downloaded_file = download_file(
                    self.app,
                    lambda percent, text: self.signals.status.emit(
                        self.app.name, percent, text),
                )
                self.signals.status.emit(self.app.name, 95, "下载完成，准备提示")
                open_download_dir()
                if sys.platform == "win32":
                    subprocess.run(
                        ['explorer', '/select,', str(downloaded_file)])
                self.signals.done.emit(
                    self.app.name, 100, "DOWNLOAD_MANUAL_HINT")
                return

            # 2. 常规下载
            downloaded_file = download_file(
                self.app,
                lambda percent, text: self.signals.status.emit(
                    self.app.name, percent, text),
            )

            # 3. 处理解压包
            if self.app.unzip:
                self.signals.status.emit(self.app.name, 92, "正在解压到桌面")
                extract_to_desktop(downloaded_file, self.app.name)
                self.signals.done.emit(self.app.name, 100, "已解压到桌面")
                return

            # 4. 处理绿色单文件 (Portable)
            if self.app.portable:
                self.signals.status.emit(self.app.name, 92, "正在部署绿色版软件")
                deploy_portable_app(
                    downloaded_file, self.app.name, self.target_drive)
                self.signals.done.emit(self.app.name, 100, "已部署并创建快捷方式")
                return

            # 5. 常规静默安装
            command = build_install_command(
                downloaded_file, self.app.install_command, self.target_drive, self.app.name)

            self.signals.status.emit(self.app.name, 94, "正在静默安装")
            result = subprocess.run(
                command, check=False, creationflags=get_creation_flags())

            if result.returncode == 0:
                self.signals.done.emit(self.app.name, 100, "安装完成")
            else:
                self.signals.error.emit(
                    self.app.name, 94, f"安装退出码 {result.returncode}")
        except Exception as exc:
            self.signals.error.emit(self.app.name, 0, str(exc))


class AppCard(QFrame):
    changed = Signal(str, bool)

    def __init__(self, app: AppItem) -> None:
        super().__init__()
        self.app = app
        self.setObjectName("appCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(12)
        self.checkbox = ModernCheckBox(app.name)
        self.checkbox.setObjectName("appCheck")
        self.checkbox.stateChanged.connect(self.on_changed)
        top.addWidget(self.checkbox, 1)

        # 根据 note 或类型显示不同的 badge
        if app.note:
            badge = QLabel(app.note if len(app.note) < 10 else "特殊安装")
            badge.setStyleSheet(
                "color: #991b1b; background: #fecaca; border: 1px solid #f87171; border-radius: 12px; padding: 5px 10px; font-size: 12px;")
        elif app.portable:
            badge = QLabel("绿色版")
            badge.setStyleSheet(
                "color: #1e3a8a; background: #dbeafe; border: 1px solid #60a5fa; border-radius: 12px; padding: 5px 10px; font-size: 12px;")
        else:
            badge = QLabel("解压到桌面" if app.unzip else "静默安装")
            badge.setObjectName("badge")

        top.addWidget(badge, 0, Qt.AlignRight)
        layout.addLayout(top)

        url = app.url if len(app.url) <= 128 else app.url[:125] + "..."
        self.url_label = QLabel(url)
        self.url_label.setObjectName("mutedText")
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.url_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        self.status = QLabel("等待选择")
        self.status.setObjectName("statusText")
        layout.addWidget(self.status)

    def on_changed(self, state: int) -> None:
        self.changed.emit(self.app.name, state == Qt.Checked.value)

    def set_selected(self, selected: bool) -> None:
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(selected)
        self.checkbox.blockSignals(False)

    def set_status(self, percent: int, text: str) -> None:
        self.progress.setValue(percent)
        self.status.setText(text)


class NewPcSetupWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.apps = load_apps()
        self.filtered_apps = list(self.apps)
        self.selected = {app.name: False for app in self.apps}
        self.progress = {app.name: 0 for app in self.apps}
        self.status = {app.name: "等待选择" for app in self.apps}
        self.cards: dict[str, AppCard] = {}
        self.running = False
        self.completed_count = 0
        self.total_jobs = 0
        self.log_lines = ["准备就绪。"]

        # 磁盘选择相关
        self.available_ssd_drives = []
        self.selected_drive = ""

        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(MAX_WORKERS)
        self.setWindowTitle(APP_TITLE)
        self.resize(1770, 1170)
        self.setMinimumSize(1020, 680)
        self.apply_style()
        self.build_ui()
        self.refresh_cards()

        # 初始化磁盘检测
        self.init_disk_selection()

    def init_disk_selection(self):
        """检测 SSD 并填充下拉框"""
        self.available_ssd_drives = get_ssd_drives()

        if not self.available_ssd_drives:
            self.drive_combo.setVisible(False)
            self.drive_label.setText("未检测到非C盘SSD，将使用默认路径")
            self.selected_drive = ""
        else:
            best_drive = self.available_ssd_drives[0]['drive']
            self.selected_drive = best_drive
            self.drive_combo.clear()
            for d in self.available_ssd_drives:
                self.drive_combo.addItem(
                    f"{d['drive']} (SSD, 剩余 {d['free_gb']:.1f} GB)", d['drive'])
            self.drive_combo.setCurrentIndex(0)
            self.drive_label.setText("选择安装盘符 (SSD):")

    def apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget#root {
                background: #10141c;
                color: #f4f7fb;
                font-family: "Microsoft YaHei UI", "Segoe UI";
            }
            QWidget#scrollContent {
                background: #10141c;
            }
            QFrame#sidePanel {
                background: #f8fafc;
                border: 1px solid #dce4ef;
                border-radius: 22px;
            }
            QFrame#appCard {
                background: #1b2432;
                border: 1px solid #3b475a;
                border-radius: 20px;
            }
            QFrame#appCard:hover {
                background: #223047;
                border-color: #5eead4;
            }
            QLabel#title {
                color: #f8fafc;
                font-size: 28px;
                font-weight: 800;
            }
            QLabel#subtitle, QLabel#mutedText, QLabel#sideText {
                color: #687385;
                font-size: 13px;
            }
            QLabel#subtitle {
                color: #b8c5d8;
            }
            QLabel#sectionTitle {
                color: #f5f8fc;
                font-size: 18px;
                font-weight: 700;
            }
            QFrame#sidePanel QLabel#sectionTitle {
                color: #111827;
            }
            QFrame#sidePanel QLabel#sideText {
                color: #475569;
            }
            QLabel#statusText {
                color: #d7e0ee;
                font-size: 12px;
            }
            QLabel#badge {
                color: #063a33;
                background: #ccfbf1;
                border: 1px solid #5eead4;
                border-radius: 12px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                background: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 15px;
                color: #111827;
                padding: 12px 14px;
                font-size: 14px;
                selection-background-color: #38d6ad;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #38d6ad;
                background: #ffffff;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #cbd5e1;
                border-left-style: solid;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
            }
            QPushButton {
                border: 0;
                border-radius: 15px;
                padding: 12px 18px;
                font-size: 14px;
                font-weight: 700;
                color: #111827;
                background: #e2e8f0;
            }
            QPushButton:hover {
                background: #cbd5e1;
            }
            QPushButton:pressed {
                background: #b8c4d4;
                padding-top: 14px;
                padding-bottom: 10px;
            }
            QPushButton#primaryButton {
                color: #06110d;
                background: #48d7ad;
            }
            QPushButton#primaryButton:hover {
                background: #5cebc0;
            }
            QPushButton#primaryButton:disabled {
                color: #7a918a;
                background: #254239;
            }
            ModernCheckBox#appCheck {
                color: #f8fafc;
                font-size: 16px;
                font-weight: 700;
                spacing: 14px;
            }
            QProgressBar {
                height: 10px;
                background: #334155;
                border: 0;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background: #48d7ad;
                border-radius: 5px;
            }
            QScrollArea {
                border: 0;
                background: #10141c;
            }
            QScrollBar:vertical {
                width: 12px;
                background: transparent;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #344155;
                border-radius: 6px;
                min-height: 48px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            """
        )

    def build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        shell = QVBoxLayout(root)
        shell.setContentsMargins(28, 26, 28, 24)
        shell.setSpacing(22)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel(APP_TITLE)
        title.setObjectName("title")
        subtitle = QLabel("给刚拿到新电脑的小白准备的一键装机清单")
        subtitle.setObjectName("subtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box, 1)

        self.start_button = AnimatedButton("开始安装")
        self.start_button.setObjectName("primaryButton")
        self.start_button.clicked.connect(self.start_install)
        header.addWidget(self.start_button, 0, Qt.AlignRight | Qt.AlignVCenter)
        shell.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(22)
        shell.addLayout(content, 1)

        side = QFrame()
        side.setObjectName("sidePanel")
        side.setFixedWidth(290)
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(14)
        content.addWidget(side)

        side_title = QLabel("控制台")
        side_title.setObjectName("sectionTitle")
        side_layout.addWidget(side_title)

        side_text = QLabel("筛选、选择，然后交给后台线程并发处理。")
        side_text.setObjectName("sideText")
        side_text.setWordWrap(True)
        side_layout.addWidget(side_text)

        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索软件")
        self.search.textChanged.connect(self.apply_filter)
        side_layout.addWidget(self.search)

        # --- 新增：盘符选择区域 ---
        self.drive_label = QLabel("检测磁盘中...")
        self.drive_label.setObjectName("sideText")
        side_layout.addWidget(self.drive_label)

        self.drive_combo = QComboBox()
        self.drive_combo.currentTextChanged.connect(self.on_drive_changed)
        side_layout.addWidget(self.drive_combo)
        # -----------------------

        self.select_all_button = AnimatedButton("全选当前列表")
        self.select_all_button.clicked.connect(self.select_all)
        side_layout.addWidget(self.select_all_button)

        self.clear_button = AnimatedButton("清空当前列表")
        self.clear_button.clicked.connect(self.clear_selection)
        side_layout.addWidget(self.clear_button)

        self.download_button = AnimatedButton("打开下载目录")
        self.download_button.clicked.connect(open_download_dir)
        side_layout.addWidget(self.download_button)

        self.selected_label = QLabel("已选择 0 个")
        self.selected_label.setObjectName("sectionTitle")
        side_layout.addSpacing(10)
        side_layout.addWidget(self.selected_label)

        worker_label = QLabel(f"并发下载：{MAX_WORKERS}")
        worker_label.setObjectName("sideText")
        side_layout.addWidget(worker_label)

        github = QLabel(f"GitHub: {GITHUB_URL}")
        github.setObjectName("sideText")
        github.setWordWrap(True)
        github.setTextInteractionFlags(Qt.TextSelectableByMouse)
        side_layout.addWidget(github)
        side_layout.addStretch(1)

        footer = QLabel(COPYRIGHT)
        footer.setObjectName("sideText")
        footer.setWordWrap(True)
        side_layout.addWidget(footer)

        main = QVBoxLayout()
        main.setSpacing(12)
        content.addLayout(main, 1)

        list_header = QHBoxLayout()
        list_title = QLabel("软件列表")
        list_title.setObjectName("sectionTitle")
        list_header.addWidget(list_title)
        self.overall_label = QLabel("等待开始")
        self.overall_label.setObjectName("subtitle")
        list_header.addWidget(self.overall_label, 0, Qt.AlignRight)
        main.addLayout(list_header)

        self.overall_bar = QProgressBar()
        self.overall_bar.setRange(0, 100)
        self.overall_bar.setTextVisible(False)
        main.addWidget(self.overall_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.card_layout = QVBoxLayout(self.scroll_content)
        self.card_layout.setContentsMargins(0, 2, 8, 2)
        self.card_layout.setSpacing(12)
        self.card_layout.addStretch(1)
        self.scroll.setWidget(self.scroll_content)
        main.addWidget(self.scroll, 1)

        log_title = QLabel("运行日志")
        log_title.setObjectName("sectionTitle")
        main.addWidget(log_title)

        self.log_box = QLabel("准备就绪。")
        self.log_box.setObjectName("mutedText")
        self.log_box.setMinimumHeight(92)
        self.log_box.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.log_box.setWordWrap(True)
        self.log_box.setStyleSheet(
            "background:#151a23;border:1px solid #252d3a;border-radius:18px;padding:14px;font-family:Consolas;"
        )
        main.addWidget(self.log_box)

    def on_drive_changed(self, text: str):
        if self.available_ssd_drives:
            self.selected_drive = self.drive_combo.currentData()

    def refresh_cards(self) -> None:
        while self.card_layout.count() > 1:
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.cards.clear()

        for app in self.filtered_apps:
            card = AppCard(app)
            card.set_selected(self.selected[app.name])
            card.set_status(self.progress[app.name], self.status[app.name])
            card.changed.connect(self.toggle_selection)
            self.card_layout.insertWidget(self.card_layout.count() - 1, card)
            self.cards[app.name] = card
        self.update_selected_label()

    def apply_filter(self) -> None:
        keyword = self.search.text().strip().lower()
        self.filtered_apps = [app for app in self.apps if keyword in app.name.lower(
        )] if keyword else list(self.apps)
        self.refresh_cards()

    def toggle_selection(self, name: str, selected: bool) -> None:
        self.selected[name] = selected
        if self.status.get(name) in {"等待选择", "已选择，等待开始"}:
            text = "已选择，等待开始" if selected else "等待选择"
            self.set_card_status(name, 0, text)
        self.update_selected_label()

    def select_all(self) -> None:
        for app in self.filtered_apps:
            self.selected[app.name] = True
            if self.status.get(app.name) in {"等待选择", "已选择，等待开始"}:
                self.progress[app.name] = 0
                self.status[app.name] = "已选择，等待开始"
        self.refresh_cards()

    def clear_selection(self) -> None:
        for app in self.filtered_apps:
            self.selected[app.name] = False
            if self.status.get(app.name) in {"等待选择", "已选择，等待开始"}:
                self.progress[app.name] = 0
                self.status[app.name] = "等待选择"
        self.refresh_cards()

    def update_selected_label(self) -> None:
        count = sum(1 for selected in self.selected.values() if selected)
        self.selected_label.setText(f"已选择 {count} 个")

    def start_install(self) -> None:
        if self.running:
            return

        selected_apps = [app for app in self.apps if self.selected[app.name]]
        if not selected_apps:
            QMessageBox.information(self, APP_TITLE, "先选几个软件，再开始安装。")
            return

        self.running = True
        self.completed_count = 0
        self.total_jobs = len(selected_apps)
        self.start_button.setEnabled(False)
        self.overall_bar.setValue(0)
        self.overall_label.setText(f"0 / {self.total_jobs} 已完成")
        self.log(f"开始处理 {self.total_jobs} 个软件。")
        if self.selected_drive:
            self.log(f"目标安装盘符: {self.selected_drive}")

        for app in selected_apps:
            self.set_card_status(app.name, 0, "排队中")
            worker = InstallWorker(app, self.selected_drive)
            worker.signals.status.connect(self.set_card_status)
            worker.signals.done.connect(self.finish_job)
            worker.signals.error.connect(self.finish_job)
            self.thread_pool.start(worker)

    @Slot(str, int, str)
    def set_card_status(self, name: str, percent: int, text: str) -> None:
        self.progress[name] = percent
        self.status[name] = text
        card = self.cards.get(name)
        if card:
            card.set_status(percent, text)
        if percent in {2, 50, 90, 94}:
            self.log(f"{name}: {text}")

    @Slot(str, int, str)
    def finish_job(self, name: str, percent: int, text: str) -> None:
        self.set_card_status(name, percent, text)
        self.completed_count += 1

        if text == "DOWNLOAD_MANUAL_HINT":
            self.log(f"{name}: 已下载，请手动安装")
            QMessageBox.information(
                self,
                f"{name} 下载完成",
                f"由于 {name} 不支持静默安装，\n"
                f"我们已经为您打开了下载文件夹并选中了安装包。\n\n"
                f"请双击运行安装包，按照提示手动完成安装。"
            )
        else:
            self.log(f"{name}: {text}")

        overall = int((self.completed_count / max(self.total_jobs, 1)) * 100)
        self.overall_bar.setValue(overall)
        self.overall_label.setText(
            f"{self.completed_count} / {self.total_jobs} 已完成")

        if self.completed_count >= self.total_jobs:
            self.running = False
            self.start_button.setEnabled(True)
            self.overall_label.setText("全部任务结束")
            self.log("所有任务已结束。")

    def log(self, text: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.log_lines.append(f"[{timestamp}] {text}")
        self.log_lines = self.log_lines[-5:]
        self.log_box.setText("\n".join(self.log_lines))

    def closeEvent(self, event) -> None:
        if self.running:
            result = QMessageBox.question(self, APP_TITLE, "任务还在后台运行，确定退出吗？")
            if result != QMessageBox.Yes:
                event.ignore()
                return
        self.thread_pool.clear()
        event.accept()


def configure_windows_dpi() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def is_admin() -> bool:
    """检查当前进程是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin() -> None:
    """以管理员身份重启当前脚本"""
    if sys.platform != "win32":
        return

    python_exe = sys.executable
    script_path = sys.argv[0]

    # 构建参数
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])

    # 使用 ShellExecuteW 触发 UAC 提权
    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        python_exe,
        f'"{script_path}" {params}',
        None,
        1  # SW_SHOWNORMAL
    )

    # 如果提权成功，ShellExecuteW 返回大于 32 的值
    if ret > 32:
        sys.exit(0)  # 退出当前非特权进程
    else:
        print("Failed to elevate privileges.")
        sys.exit(1)


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def app_list_candidates() -> list[Path]:
    candidates = [app_base_dir() / "app-list.json"]
    bundled_dir = getattr(sys, "_MEIPASS", None)
    if bundled_dir:
        candidates.append(Path(bundled_dir) / "app-list.json")
    return candidates


def get_huorong_latest_url() -> str:
    """
    从火绒官方接口获取最新 x64 版本下载链接
    """
    url = "https://www.huorong.cn/product/versionShow60.php"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            latest_url = data.get('x64UrlAll', '')
            if latest_url:
                print(f"[Info] 获取到火绒最新版本链接: {latest_url}")
                return latest_url
    except Exception as e:
        print(f"[Error] 获取火绒版本失败: {e}")
    return ""


def load_apps() -> list[AppItem]:
    raw_apps = EMBEDDED_APP_LIST
    for source in app_list_candidates():
        if not source.exists():
            continue
        try:
            raw_apps = json.loads(source.read_text(encoding="utf-8"))
            break
        except Exception:
            break

    huorong_url = get_huorong_latest_url()

    apps = []
    for raw in raw_apps:
        name = str(raw.get("name", "")).strip()
        url = str(raw.get("URL") or raw.get("url") or "").strip()

        if name == "火绒安全" and huorong_url:
            url = huorong_url

        if not name or not url:
            continue
        apps.append(
            AppItem(
                name=name,
                url=url,
                unzip=as_bool(raw.get("unzip", False)),
                install_command=str(raw.get("install-command", "")).strip(),
                note=str(raw.get("note", "")).strip(),
                portable=as_bool(raw.get("portable", False)),
            )
        )
    return apps


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def download_root() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if base:
        root = Path(base) / "Mete0rNewPcHelper" / "downloads"
    else:
        root = Path(tempfile.gettempdir()) / "Mete0rNewPcHelper" / "downloads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def safe_filename_from_url(url: str, fallback: str) -> str:
    parsed = urllib.parse.urlparse(url)
    filename = Path(urllib.parse.unquote(parsed.path)).name
    if not filename or "." not in filename:
        filename = f"{fallback}.bin"
    invalid = '<>:"/\\|?*'
    return "".join("_" if char in invalid else char for char in filename)


def download_file(app: AppItem, progress_callback) -> Path:
    target = download_root() / safe_filename_from_url(app.url, app.name)
    request = urllib.request.Request(
        app.url, headers={"User-Agent": "Mete0rNewPcHelper/0.2"})
    with urllib.request.urlopen(request, timeout=45) as response:
        total = int(response.headers.get("Content-Length") or 0)
        downloaded = 0
        with target.open("wb") as file:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                file.write(chunk)
                downloaded += len(chunk)
                if total:
                    percent = min(90, int(downloaded / total * 90))
                    progress_callback(
                        percent, f"下载中 {format_bytes(downloaded)} / {format_bytes(total)}")
                else:
                    progress_callback(25, f"下载中 {format_bytes(downloaded)}")
    progress_callback(90, "下载完成")
    return target


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} GB"


def desktop_dir() -> Path:
    return Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"


def extract_to_desktop(zip_path: Path, app_name: str) -> None:
    target = desktop_dir() / app_name
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target)


def create_shortcut(target_path: Path, link_name: str) -> None:
    """
    在桌面创建快捷方式，不使用额外库
    """
    desktop = desktop_dir()
    link_path = desktop / f"{link_name}.lnk"

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(link_path))
        shortcut.Targetpath = str(target_path)
        shortcut.WorkingDirectory = str(target_path.parent)
        shortcut.save()
    except ImportError:
        # 降级方案：创建 .bat 启动器
        bat_path = desktop / f"{link_name}.bat"
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(f"@echo off\nstart \"\" \"{target_path}\"\n")
        print(f"[Warning] pywin32 not found, created .bat launcher instead of .lnk")


def deploy_portable_app(source_file: Path, app_name: str, target_drive: str) -> None:
    """
    部署绿色单文件软件：
    1. 移动到目标盘符的指定目录
    2. 创建桌面快捷方式
    """
    if not target_drive:
        target_dir = Path(os.environ.get(
            "PROGRAMFILES", "C:\\Program Files")) / app_name
    else:
        target_dir = Path(target_drive + "\\") / app_name

    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / source_file.name

    # 移动文件
    shutil.move(str(source_file), str(target_file))

    # 创建快捷方式
    create_shortcut(target_file, app_name)


def get_ssd_drives() -> list[dict]:
    """
    检测除 C 盘外的所有 SSD 盘符，并按剩余空间从大到小排序。
    """
    if sys.platform != "win32":
        return []

    drives = []
    for letter_ord in range(ord('D'), ord('Z') + 1):
        letter = chr(letter_ord)
        drive_path = f"{letter}:\\"

        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
        if drive_type != 3:
            continue

        handle = ctypes.windll.kernel32.CreateFileW(
            f"\\\\.\\{letter}:",
            0,
            0x00000001 | 0x00000002,
            None,
            3,
            0,
            None
        )

        is_ssd = False
        if handle != -1:
            is_ssd = True
            ctypes.windll.kernel32.CloseHandle(handle)

        if is_ssd:
            try:
                free_bytes = ctypes.c_ulonglong(0)
                total_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    drive_path,
                    ctypes.byref(free_bytes),
                    ctypes.byref(total_bytes),
                    None
                )
                free_gb = free_bytes.value / (1024**3)
                drives.append({'drive': f"{letter}:", 'free_gb': free_gb})
            except:
                continue

    drives.sort(key=lambda x: x['free_gb'], reverse=True)
    return drives


def build_install_command(installer: Path, install_command: str, target_drive: str, app_name: str) -> list[str]:
    """
    构建安装命令，智能追加路径参数。
    """
    command = [str(installer)]

    if not target_drive:
        if install_command:
            command.extend(shlex.split(install_command, posix=False))
        return command

    target_path = os.path.join(target_drive + "\\", app_name)
    target_path = target_path.replace('/', '\\')

    base_cmd = install_command

    path_pattern = r'[A-Z]:\\[^"\s]+'
    if re.search(path_pattern, base_cmd):
        new_cmd = re.sub(path_pattern, target_path.replace(
            '\\', '\\\\'), base_cmd, count=1)
        command.extend(shlex.split(new_cmd, posix=False))
        return command

    if "/NCRC" in base_cmd:
        final_cmd = f"{base_cmd} /D={target_path}"
    elif "/VERYSILENT" in base_cmd or "/SILENT" in base_cmd:
        final_cmd = f'{base_cmd} /DIR="{target_path}"'
    elif "/S" in base_cmd:
        final_cmd = f"{base_cmd} /D={target_path}"
    else:
        final_cmd = f'{base_cmd} /DIR="{target_path}"'

    command.extend(shlex.split(final_cmd, posix=False))
    return command


def get_creation_flags() -> int:
    if sys.platform != "win32":
        return 0
    return subprocess.CREATE_NO_WINDOW


def open_download_dir() -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(download_root())))


def main() -> None:
    # --- 自动提权逻辑 ---
    if sys.platform == "win32" and not is_admin():
        run_as_admin()
    # ------------------

    configure_windows_dpi()
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    window = NewPcSetupWindow()
    QTimer.singleShot(0, window.show)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
