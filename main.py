import sys
import os
import datetime
import winreg
from PyQt6.QtCore import (
    Qt, QTimer, QPoint, QRect, QTime
)
from PyQt6.QtGui import (
    QAction, QPainter, QColor, QPen, QMouseEvent, QFont, QIcon, QPixmap
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMenu, QMessageBox,
    QDialog, QVBoxLayout, QLabel, QTimeEdit, QPushButton,
    QSlider, QHBoxLayout, QSpinBox, QSystemTrayIcon
)


# ------------------------------
# 语言文本
# ------------------------------
TEXTS = {
    'zh': {
        'set_time': '设置时间段',
        'set_size': '设置大小',
        'set_opacity': '设置透明度',
        'snap': '吸附开关',
        'topmost': '置顶开关',
        'ticks': '显示刻度',
        'autostart': '开机自启',
        'language': '语言/Language',
        'time_range_title': '设置时间段',
        'start_time': '开始时间 (HH:MM)',
        'end_time': '结束时间 (HH:MM)',
        'ok': '确定',
        'size_title': '设置大小',
        'width': '宽度:',
        'height': '高度:',
        'opacity_title': '设置透明度 (0-100)',
        'success': '成功',
        'failed': '失败',
        'error': '错误',
        'autostart_on': '已设置开机自启',
        'autostart_off': '已取消开机自启',
        'autostart_failed': '操作失败',
        'show_hide': '显示/隐藏',
        'quit': '退出',
    },
    'en': {
        'set_time': 'Set Time Range',
        'set_size': 'Set Size',
        'set_opacity': 'Set Opacity',
        'snap': 'Snap',
        'topmost': 'Always on Top',
        'ticks': 'Show Ticks',
        'autostart': 'Auto-start',
        'language': 'Language/语言',
        'time_range_title': 'Set Time Range',
        'start_time': 'Start Time (HH:MM)',
        'end_time': 'End Time (HH:MM)',
        'ok': 'OK',
        'size_title': 'Set Size',
        'width': 'Width:',
        'height': 'Height:',
        'opacity_title': 'Set Opacity (0-100)',
        'success': 'Success',
        'failed': 'Failed',
        'error': 'Error',
        'autostart_on': 'Auto-start enabled',
        'autostart_off': 'Auto-start disabled',
        'autostart_failed': 'Operation failed',
        'show_hide': 'Show/Hide',
        'quit': 'Quit',
    }
}


# ------------------------------
# 时间段设置对话框
# ------------------------------
class TimeRangeDialog(QDialog):
    def __init__(self, start_time: str, end_time: str, lang: str = 'zh', parent=None):
        super().__init__(parent)
        try:
            self.lang = lang
            self.texts = TEXTS[lang]
            self.setWindowTitle(self.texts['time_range_title'])
            
            # 设置窗口标志，确保对话框可见
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
            
            # 设置最小尺寸
            self.setMinimumWidth(300)

            layout = QVBoxLayout()

            self.label1 = QLabel(self.texts['start_time'])
            self.start_edit = QTimeEdit()
            self.start_edit.setDisplayFormat("HH:mm")
            h, m = map(int, start_time.split(":"))
            self.start_edit.setTime(QTime(h, m))

            self.label2 = QLabel(self.texts['end_time'])
            self.end_edit = QTimeEdit()
            self.end_edit.setDisplayFormat("HH:mm")
            h, m = map(int, end_time.split(":"))
            self.end_edit.setTime(QTime(h, m))

            self.ok_btn = QPushButton(self.texts['ok'])
            self.ok_btn.clicked.connect(self.accept)

            layout.addWidget(self.label1)
            layout.addWidget(self.start_edit)
            layout.addWidget(self.label2)
            layout.addWidget(self.end_edit)
            layout.addWidget(self.ok_btn)

            self.setLayout(layout)
            
            # 如果有父窗口，将对话框居中显示在父窗口附近
            if parent:
                parent_rect = parent.geometry()
                self.move(parent_rect.center().x() - 150, parent_rect.center().y() - 100)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise

    def get_times(self):
        return (
            self.start_edit.time().toString("HH:mm"),
            self.end_edit.time().toString("HH:mm")
        )


# ------------------------------
# 主圆角进度条窗口
# ------------------------------
class ProgressWidget(QWidget):
    def __init__(self):
        super().__init__()

        # 默认参数
        self.start_time = "10:00"
        self.end_time = "22:00"
        self.opacity = 0.7
        self.bar_height = 60
        self.show_ticks = True
        self.is_topmost = True
        self.snap_enabled = True
        self.language = 'zh'  # 默认中文
        self.texts = TEXTS[self.language]

        self.resize(700, self.bar_height)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.is_topmost)
        self.setWindowFlag(Qt.WindowType.Tool)  # 不在任务栏显示
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 拖动用
        self.dragging = False
        self.drag_offset = QPoint()

        # 创建系统托盘图标
        self.create_tray_icon()

        # 更新计时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        # 右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)

    # ------------------------------
    # 系统托盘图标
    # ------------------------------
    def create_tray_icon(self):
        """创建系统托盘图标"""
        # 创建一个简单的图标（蓝色圆形）
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(0, 122, 204))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        painter.end()
        
        icon = QIcon(pixmap)
        
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("ProgressBar")
        
        # 托盘菜单
        self.update_tray_menu()
        
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def update_tray_menu(self):
        """更新托盘菜单（支持语言切换）"""
        tray_menu = QMenu()
        
        show_action = QAction(self.texts['show_hide'], self)
        show_action.triggered.connect(self.toggle_visibility)
        
        quit_action = QAction(self.texts['quit'], self)
        quit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)

    def tray_icon_activated(self, reason):
        """托盘图标被点击"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visibility()

    def toggle_visibility(self):
        """切换窗口显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def quit_app(self):
        """退出应用"""
        self.tray_icon.hide()
        QApplication.quit()

    # ------------------------------
    # 时间计算
    # ------------------------------
    def get_progress(self):
        now = datetime.datetime.now().time()
        sh, sm = map(int, self.start_time.split(":"))
        eh, em = map(int, self.end_time.split(":"))

        start = datetime.time(sh, sm)
        end = datetime.time(eh, em)

        # 跨天情况自动处理
        today = datetime.date.today()
        dt_start = datetime.datetime.combine(today, start)
        dt_end = datetime.datetime.combine(today, end)
        dt_now = datetime.datetime.combine(today, now)

        if dt_now < dt_start:
            return 0
        if dt_now > dt_end:
            return 1

        total = (dt_end - dt_start).total_seconds()
        used = (dt_now - dt_start).total_seconds()
        return used / total if total > 0 else 0

    # ------------------------------
    # 绘制外观
    # ------------------------------
    def paintEvent(self, event):
        progress = self.get_progress()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 背景
        bg_color = QColor(20, 20, 20, int(self.opacity * 255))
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)
        
        # 进度条
        bar_rect = QRect(5, 5, int((self.width() - 10) * progress), self.height() - 10)
        painter.setBrush(QColor(0, 122, 204, int(self.opacity * 255)))
        painter.drawRoundedRect(bar_rect, 10, 10)

        # 刻度
        if self.show_ticks:
            pen = QPen(QColor(255, 255, 255, 120))
            pen.setWidth(2)
            painter.setPen(pen)

            segments = 12  # 刻度数量
            for i in range(segments + 1):
                x = 5 + (self.width() - 10) * i / segments
                painter.drawLine(int(x), self.height() - 5, int(x), self.height())

        # 显示时间和百分比
        now = datetime.datetime.now().time()
        time_str = now.strftime("%H:%M")
        progress_str = f"{time_str} {int(progress * 100)}%"
        
        font = QFont()
        font.setPointSize(14)  # 设置字体大小为14点
        font.setBold(True)     # 设置为粗体
        painter.setFont(font)
        
        painter.setPen(QColor(255, 255, 255, 220))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, progress_str)

        painter.end()

    # ------------------------------
    # 鼠标拖动
    # ------------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_offset = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False

        # 自动吸附
        if self.snap_enabled:
            g = QApplication.primaryScreen().geometry()

            x, y = self.x(), self.y()
            margin = 50  # 吸附边距

            # 吸附到左边
            if abs(x) < margin:
                x = 0
            # 吸附到右边
            if abs((x + self.width()) - g.width()) < margin:
                x = g.width() - self.width()
            
            # 吸附到顶部
            if abs(y) < margin:
                y = 0
            # 吸附到底部
            if abs((y + self.height()) - g.height()) < margin:
                y = g.height() - self.height()
            
            self.move(x, y)

    # ------------------------------
    # 右键菜单
    # ------------------------------
    def show_menu(self, pos):
        menu = QMenu(self)

        act_time = QAction(self.texts['set_time'], self)
        act_size = QAction(self.texts['set_size'], self)
        act_opacity = QAction(self.texts['set_opacity'], self)
        act_snap = QAction(self.texts['snap'], self)
        act_snap.setCheckable(True)
        act_snap.setChecked(self.snap_enabled)
        act_top = QAction(self.texts['topmost'], self)
        act_top.setCheckable(True)
        act_top.setChecked(self.is_topmost)
        act_ticks = QAction(self.texts['ticks'], self)
        act_ticks.setCheckable(True)
        act_ticks.setChecked(self.show_ticks)
        act_autostart = QAction(self.texts['autostart'], self)
        act_autostart.setCheckable(True)
        act_autostart.setChecked(self.check_autostart())
        act_language = QAction(self.texts['language'], self)

        menu.addAction(act_time)
        menu.addAction(act_size)
        menu.addAction(act_opacity)
        menu.addAction(act_snap)
        menu.addAction(act_top)
        menu.addAction(act_ticks)
        menu.addSeparator()
        menu.addAction(act_autostart)
        menu.addAction(act_language)

        act_time.triggered.connect(self.edit_time)
        act_size.triggered.connect(self.edit_size)
        act_opacity.triggered.connect(self.edit_opacity)
        act_snap.triggered.connect(self.toggle_snap)
        act_top.triggered.connect(self.toggle_top)
        act_ticks.triggered.connect(self.toggle_ticks)
        act_autostart.triggered.connect(self.toggle_autostart)
        act_language.triggered.connect(self.toggle_language)

        menu.exec(self.mapToGlobal(pos))

    # ------------------------------
    # 菜单功能
    # ------------------------------
    def edit_time(self):
        try:
            dlg = TimeRangeDialog(self.start_time, self.end_time, self.language, self)
            result = dlg.exec()
            if result == QDialog.DialogCode.Accepted:
                self.start_time, self.end_time = dlg.get_times()
                self.update()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Time setting error: {str(e)}\n{type(e).__name__}")
            import traceback
            traceback.print_exc()

    def edit_size(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self.texts['size_title'])
        
        layout = QVBoxLayout()
        
        # 宽度设置
        width_label = QLabel(self.texts['width'])
        width_spin = QSpinBox()
        width_spin.setMinimum(200)
        width_spin.setMaximum(2000)
        width_spin.setValue(self.width())
        
        # 高度设置
        height_label = QLabel(self.texts['height'])
        height_spin = QSpinBox()
        height_spin.setMinimum(20)
        height_spin.setMaximum(200)
        height_spin.setValue(self.bar_height)
        
        ok_btn = QPushButton(self.texts['ok'])
        ok_btn.clicked.connect(dlg.accept)
        
        layout.addWidget(width_label)
        layout.addWidget(width_spin)
        layout.addWidget(height_label)
        layout.addWidget(height_spin)
        layout.addWidget(ok_btn)
        
        dlg.setLayout(layout)
        
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.bar_height = height_spin.value()
            self.resize(width_spin.value(), self.bar_height)

    def edit_opacity(self):
        value, ok = self.get_integer(self.texts['opacity_title'], 10, 100, int(self.opacity * 100))
        if ok:
            self.opacity = value / 100
            self.update()

    def toggle_snap(self):
        self.snap_enabled = not self.snap_enabled

    def toggle_top(self):
        self.is_topmost = not self.is_topmost
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.is_topmost)
        self.show()

    def toggle_ticks(self):
        self.show_ticks = not self.show_ticks
        self.update()

    def toggle_language(self):
        """切换语言"""
        self.language = 'en' if self.language == 'zh' else 'zh'
        self.texts = TEXTS[self.language]
        self.update_tray_menu()  # 更新托盘菜单
        self.update()

    def check_autostart(self):
        """检查是否已设置开机自启"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "ProgressBar")
                winreg.CloseKey(key)
                return True
            except WindowsError:
                winreg.CloseKey(key)
                return False
        except:
            return False

    def toggle_autostart(self):
        """切换开机自启状态"""
        app_name = "ProgressBar"
        app_path = os.path.abspath(sys.argv[0])
        
        # 如果是打包后的exe，使用exe路径；否则使用Python脚本路径
        if getattr(sys, 'frozen', False):
            app_path = sys.executable
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Run",
                                0, winreg.KEY_ALL_ACCESS)
            
            if self.check_autostart():
                # 删除自启动项
                try:
                    winreg.DeleteValue(key, app_name)
                    QMessageBox.information(self, self.texts['success'], self.texts['autostart_off'])
                except:
                    QMessageBox.warning(self, self.texts['failed'], self.texts['autostart_failed'])
            else:
                # 添加自启动项
                try:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{app_path}"')
                    QMessageBox.information(self, self.texts['success'], self.texts['autostart_on'])
                except:
                    QMessageBox.warning(self, self.texts['failed'], self.texts['autostart_failed'])
            
            winreg.CloseKey(key)
        except Exception as e:
            QMessageBox.warning(self, self.texts['error'], f"{self.texts['autostart_failed']}: {str(e)}")

    # ------------------------------
    # 输入框（整数）
    # ------------------------------
    def get_integer(self, title, min_val, max_val, default):
        dlg = QDialog(self)
        dlg.setWindowTitle(title)

        layout = QVBoxLayout()

        spin = QSpinBox()
        spin.setMinimum(min_val)
        spin.setMaximum(max_val)
        spin.setValue(default)

        ok_btn = QPushButton(self.texts['ok'])
        ok_btn.clicked.connect(dlg.accept)

        layout.addWidget(spin)
        layout.addWidget(ok_btn)

        dlg.setLayout(layout)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            return spin.value(), True
        return default, False


# ------------------------------
# 运行
# ------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ProgressWidget()
    w.show()
    sys.exit(app.exec())
