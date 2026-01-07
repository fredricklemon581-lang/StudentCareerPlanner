# -*- coding: utf-8 -*-
"""
🍎 Apple风格设计系统
Design System Foundation for StudentCareerPlanner
"""
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget
from PyQt6.QtGui import QColor, QFont


# ═══════════════════════════════════════════════════════════════
# 🎨 色彩系统 (Color System)
# ═══════════════════════════════════════════════════════════════

class Colors:
    """Apple风格色彩"""
    
    # 主色调
    PRIMARY = "#007AFF"       # Apple Blue
    PRIMARY_DARK = "#0055CC"
    PRIMARY_LIGHT = "#4DA3FF"
    
    ACCENT = "#5856D6"        # Purple
    
    # 语义色
    SUCCESS = "#34C759"       # Green - 成功/进步
    WARNING = "#FF9500"       # Orange - 警告/注意
    DANGER = "#FF3B30"        # Red - 错误/下降
    INFO = "#5AC8FA"          # Cyan - 信息
    
    # 灰度系统 (Dark Mode)
    GRAY_1 = "#8E8E93"        # 辅助文字
    GRAY_2 = "#636366"        # 次要内容
    GRAY_3 = "#48484A"        # 分割线
    GRAY_4 = "#3A3A3C"        # 卡片背景
    GRAY_5 = "#2C2C2E"        # 次级背景
    GRAY_6 = "#1C1C1E"        # 主背景
    
    # 背景
    BG_PRIMARY = "#000000"
    BG_SECONDARY = "#1C1C1E"
    BG_TERTIARY = "#2C2C2E"
    BG_ELEVATED = "#3A3A3C"
    
    # 文字
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "rgba(255,255,255,0.7)"
    TEXT_TERTIARY = "rgba(255,255,255,0.5)"
    TEXT_PLACEHOLDER = "rgba(255,255,255,0.3)"
    
    # 材质 (Vibrancy)
    MATERIAL_ULTRA_THIN = "rgba(255,255,255,0.05)"
    MATERIAL_THIN = "rgba(255,255,255,0.08)"
    MATERIAL_REGULAR = "rgba(255,255,255,0.12)"
    MATERIAL_THICK = "rgba(255,255,255,0.18)"


# ═══════════════════════════════════════════════════════════════
# 📝 字体系统 (Typography)
# ═══════════════════════════════════════════════════════════════

class Typography:
    """Apple风格字体层级"""
    
    # 字体族
    FONT_FAMILY = "SF Pro Display, PingFang SC, Microsoft YaHei, sans-serif"
    FONT_FAMILY_MONO = "SF Mono, Consolas, monospace"
    
    # 字体规格
    DISPLAY_LARGE = {"size": 48, "weight": 700, "tracking": -1.5}
    DISPLAY = {"size": 34, "weight": 700, "tracking": -0.5}
    TITLE_1 = {"size": 28, "weight": 600, "tracking": -0.3}
    TITLE_2 = {"size": 22, "weight": 600, "tracking": 0}
    TITLE_3 = {"size": 20, "weight": 600, "tracking": 0}
    HEADLINE = {"size": 17, "weight": 600, "tracking": 0}
    BODY = {"size": 15, "weight": 400, "tracking": 0}
    CALLOUT = {"size": 14, "weight": 400, "tracking": 0}
    CAPTION_1 = {"size": 12, "weight": 400, "tracking": 0}
    CAPTION_2 = {"size": 11, "weight": 400, "tracking": 0.2}
    
    @staticmethod
    def get_font(spec: dict) -> QFont:
        """获取QFont对象"""
        font = QFont()
        font.setFamily("SF Pro Display")
        font.setPixelSize(spec["size"])
        font.setWeight(QFont.Weight(spec["weight"] // 100))
        return font


# ═══════════════════════════════════════════════════════════════
# 📐 间距系统 (Spacing)
# ═══════════════════════════════════════════════════════════════

class Spacing:
    """8px网格系统"""
    
    XXXS = 2
    XXS = 4
    XS = 8
    SM = 12
    MD = 16
    LG = 24
    XL = 32
    XXL = 48
    XXXL = 64


# ═══════════════════════════════════════════════════════════════
# 🔷 圆角系统 (Border Radius)
# ═══════════════════════════════════════════════════════════════

class Radius:
    """统一圆角"""
    
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    ROUND = 999  # 圆形


# ═══════════════════════════════════════════════════════════════
# ✨ 阴影系统 (Shadows)
# ═══════════════════════════════════════════════════════════════

class Shadows:
    """深度层次"""
    
    NONE = "none"
    SUBTLE = "0 2px 8px rgba(0,0,0,0.15)"
    SMALL = "0 4px 12px rgba(0,0,0,0.2)"
    MEDIUM = "0 8px 24px rgba(0,0,0,0.25)"
    LARGE = "0 12px 36px rgba(0,0,0,0.3)"
    ELEVATED = "0 16px 48px rgba(0,0,0,0.35)"


# ═══════════════════════════════════════════════════════════════
# 🌊 动效系统 (Motion)
# ═══════════════════════════════════════════════════════════════

class Motion:
    """Apple风格动效"""
    
    # 持续时间 (ms)
    INSTANT = 100     # 微交互
    QUICK = 200       # 状态变化
    NORMAL = 350      # 页面过渡
    SLOW = 500        # 强调动画
    SLOWER = 700      # 复杂动画
    
    # 缓动曲线
    EASE_OUT = QEasingCurve.Type.OutQuad
    EASE_IN_OUT = QEasingCurve.Type.InOutQuad
    SPRING = QEasingCurve.Type.OutBack       # 弹性
    BOUNCE = QEasingCurve.Type.OutBounce     # 弹跳
    ELASTIC = QEasingCurve.Type.OutElastic   # 弹簧
    
    @staticmethod
    def fade_in(widget: QWidget, duration: int = 350) -> QPropertyAnimation:
        """淡入动画"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(Motion.EASE_OUT)
        return anim
    
    @staticmethod
    def slide_in(widget: QWidget, direction: str = "right", duration: int = 350):
        """滑入动画"""
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setEasingCurve(Motion.SPRING)
        return anim


# ═══════════════════════════════════════════════════════════════
# 🎛️ 组件样式 (Component Styles)
# ═══════════════════════════════════════════════════════════════

class Styles:
    """预定义样式"""
    
    # 主按钮
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
            color: white;
            border: none;
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.LG}px;
            font-size: 15px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {Colors.PRIMARY_LIGHT}, stop:1 {Colors.PRIMARY});
        }}
        QPushButton:pressed {{
            background: {Colors.PRIMARY_DARK};
        }}
        QPushButton:disabled {{
            background: {Colors.GRAY_4};
            color: {Colors.GRAY_2};
        }}
    """
    
    # 次级按钮
    BUTTON_SECONDARY = f"""
        QPushButton {{
            background: {Colors.MATERIAL_REGULAR};
            color: {Colors.PRIMARY};
            border: 1px solid {Colors.PRIMARY};
            border-radius: {Radius.MD}px;
            padding: {Spacing.SM}px {Spacing.LG}px;
            font-size: 15px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {Colors.MATERIAL_THICK};
        }}
    """
    
    # 卡片
    CARD = f"""
        QFrame {{
            background: {Colors.BG_TERTIARY};
            border-radius: {Radius.LG}px;
            border: 1px solid {Colors.GRAY_4};
        }}
    """
    
    # 输入框
    INPUT = f"""
        QLineEdit, QTextEdit {{
            background: {Colors.BG_TERTIARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.GRAY_4};
            border-radius: {Radius.SM}px;
            padding: {Spacing.SM}px;
            font-size: 15px;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: 2px solid {Colors.PRIMARY};
        }}
    """
    
    # 下拉框
    COMBO_BOX = f"""
        QComboBox {{
            background: {Colors.BG_TERTIARY};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.GRAY_4};
            border-radius: {Radius.SM}px;
            padding: {Spacing.XS}px {Spacing.SM}px;
            font-size: 14px;
            min-height: 36px;
        }}
        QComboBox:hover {{
            border-color: {Colors.GRAY_2};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 10px;
        }}
        QComboBox QAbstractItemView {{
            background: {Colors.BG_ELEVATED};
            color: {Colors.TEXT_PRIMARY};
            selection-background-color: {Colors.PRIMARY};
            border-radius: {Radius.SM}px;
        }}
    """
    
    # 表格
    TABLE = f"""
        QTableWidget {{
            background: {Colors.BG_TERTIARY};
            color: {Colors.TEXT_PRIMARY};
            border: none;
            border-radius: {Radius.MD}px;
            gridline-color: {Colors.GRAY_4};
        }}
        QTableWidget::item {{
            padding: {Spacing.XS}px;
            border-bottom: 1px solid {Colors.GRAY_4};
        }}
        QTableWidget::item:selected {{
            background: {Colors.PRIMARY};
            color: white;
        }}
        QHeaderView::section {{
            background: {Colors.BG_ELEVATED};
            color: {Colors.TEXT_SECONDARY};
            padding: {Spacing.SM}px;
            border: none;
            font-weight: 600;
        }}
    """
    
    # 导航按钮
    NAV_BUTTON = f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: {Radius.MD}px;
            color: {Colors.TEXT_SECONDARY};
            font-size: 15px;
            font-weight: 500;
            text-align: left;
            padding: {Spacing.SM}px {Spacing.MD}px;
            margin: 2px {Spacing.SM}px;
        }}
        QPushButton:hover {{
            background: {Colors.MATERIAL_THIN};
            color: {Colors.TEXT_PRIMARY};
        }}
        QPushButton:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
            color: white;
            font-weight: 600;
        }}
    """


# ═══════════════════════════════════════════════════════════════
# 🔧 工具函数
# ═══════════════════════════════════════════════════════════════

def apply_card_style(widget):
    """应用卡片样式"""
    widget.setStyleSheet(Styles.CARD)

def apply_button_style(button, style="primary"):
    """应用按钮样式"""
    if style == "primary":
        button.setStyleSheet(Styles.BUTTON_PRIMARY)
    else:
        button.setStyleSheet(Styles.BUTTON_SECONDARY)

def get_status_color(status: str) -> str:
    """获取状态颜色"""
    color_map = {
        "success": Colors.SUCCESS,
        "warning": Colors.WARNING,
        "danger": Colors.DANGER,
        "info": Colors.INFO,
        "neutral": Colors.GRAY_1
    }
    return color_map.get(status, Colors.GRAY_1)


# ═══════════════════════════════════════════════════════════════
# 🔄 加载状态组件 (Loading Components)
# ═══════════════════════════════════════════════════════════════

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from PyQt6.QtCore import QTimer, Qt


class LoadingSpinner(QLabel):
    """Apple风格加载指示器"""
    
    def __init__(self, text: str = "加载中...", parent=None):
        super().__init__(parent)
        self.dots = 0
        self.base_text = text.replace("...", "")
        self.setText(f"⏳ {self.base_text}")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                color: {Colors.GRAY_1};
                font-size: 14px;
                padding: 20px;
            }}
        """)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
    
    def start(self):
        self.timer.start(400)
        self.show()
    
    def stop(self):
        self.timer.stop()
        self.hide()
    
    def _animate(self):
        self.dots = (self.dots + 1) % 4
        dots_str = "." * self.dots
        self.setText(f"⏳ {self.base_text}{dots_str}")


class EmptyState(QFrame):
    """空状态引导组件"""
    
    def __init__(self, icon: str = "📭", title: str = "暂无数据", 
                 description: str = "", action_text: str = "", parent=None):
        super().__init__(parent)
        self.action_callback = None
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {Colors.BG_TERTIARY};
                border-radius: {Radius.LG}px;
                border: 1px dashed {Colors.GRAY_3};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 图标
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: 600;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet(f"""
                color: {Colors.TEXT_TERTIARY};
                font-size: 14px;
            """)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # 操作按钮
        if action_text:
            layout.addSpacing(10)
            self.action_btn = QPushButton(action_text)
            self.action_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
            self.action_btn.setMaximumWidth(200)
            layout.addWidget(self.action_btn, 0, Qt.AlignmentFlag.AlignCenter)
    
    def set_action(self, callback):
        """设置按钮点击回调"""
        if hasattr(self, 'action_btn'):
            self.action_btn.clicked.connect(callback)


class ToastNotification(QFrame):
    """轻量级Toast通知"""
    
    def __init__(self, message: str, toast_type: str = "info", parent=None):
        super().__init__(parent)
        
        # 根据类型选择样式
        colors = {
            "success": (Colors.SUCCESS, "✓"),
            "warning": (Colors.WARNING, "⚠"),
            "danger": (Colors.DANGER, "✕"),
            "info": (Colors.INFO, "ℹ")
        }
        color, icon = colors.get(toast_type, (Colors.INFO, "ℹ"))
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {color};
                border-radius: {Radius.MD}px;
                padding: 12px 20px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(icon_label)
        
        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(msg_label)
        
        # 自动隐藏定时器
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._fade_out)
    
    def show_toast(self, duration: int = 3000):
        """显示Toast"""
        self.show()
        self.hide_timer.start(duration)
    
    def _fade_out(self):
        """淡出隐藏"""
        self.hide()


# ═══════════════════════════════════════════════════════════════
# 🎯 状态卡片 (Status Cards)
# ═══════════════════════════════════════════════════════════════

class StatusCard(QFrame):
    """状态指示卡片"""
    
    def __init__(self, title: str, value: str, status: str = "neutral", 
                 icon: str = "", parent=None):
        super().__init__(parent)
        
        color = get_status_color(status)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: {Radius.LG}px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # 标题行
        header = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 20px;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Colors.GRAY_2}; font-size: 12px;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # 数值
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"""
            color: #2d3748;
            font-size: 24px;
            font-weight: 700;
        """)
        layout.addWidget(self.value_label)
    
    def update_value(self, value: str, status: str = None):
        """更新数值"""
        self.value_label.setText(value)
        if status:
            color = get_status_color(status)
            self.setStyleSheet(f"""
                QFrame {{
                    background: white;
                    border-radius: {Radius.LG}px;
                    border-left: 4px solid {color};
                }}
            """)

