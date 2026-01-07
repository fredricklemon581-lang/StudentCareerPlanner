# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, 
                           QPushButton, QHBoxLayout, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class iOSTableCell(QPushButton):
    """
    iOS风格列表项
    支持首尾圆角处理 (Inset Grouped)
    """
    def __init__(self, text, detail="", icon=None, position="middle", parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px;")
            layout.addWidget(icon_lbl)
        
        title = QLabel(text)
        title.setStyleSheet("font-size: 16px; color: #1C1C1E;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        if detail:
            det = QLabel(detail)
            det.setStyleSheet("font-size: 15px; color: #8E8E93;")
            layout.addWidget(det)
        
        # Chevron
        chevron = QLabel("›")
        chevron.setStyleSheet("font-size: 20px; color: #C7C7CC; font-weight: bold;")
        layout.addWidget(chevron)
        
        # Border Radius Logic
        radius_top = "10px" if position in ["top", "single"] else "0"
        radius_bottom = "10px" if position in ["bottom", "single"] else "0"
        
        # Bottom Border Logic
        border_bottom = "1px solid #E5E5EA" if position != "bottom" and position != "single" else "none"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: none;
                border-bottom: {border_bottom};
                border-top-left-radius: {radius_top};
                border-top-right-radius: {radius_top};
                border-bottom-left-radius: {radius_bottom};
                border-bottom-right-radius: {radius_bottom};
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #F2F2F7;
            }}
            QPushButton:pressed {{
                background-color: #E5E5EA;
            }}
        """)

class iOSTableView(QWidget):
    """
    iOS风格分组列表视图
    """
    def __init__(self, title="列表", parent=None):
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Title
        if title:
            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("font-size: 34px; font-weight: 700; color: #1C1C1E; margin-bottom: 10px;")
            self.layout.addWidget(t_lbl)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
    def add_section(self, header, items):
        """添加分组"""
        section = QWidget()
        sec_layout = QVBoxLayout(section)
        sec_layout.setContentsMargins(0, 0, 0, 0)
        sec_layout.setSpacing(0)
        
        if header:
            h_lbl = QLabel(header.upper())
            h_lbl.setStyleSheet("font-size: 13px; color: #8E8E93; margin-left: 16px; margin-bottom: 6px; font-weight: 600;")
            sec_layout.addWidget(h_lbl)
            
        # Items
        count = len(items)
        for i, item_data in enumerate(items):
            text, detail = item_data
            
            position = "middle"
            if count == 1: position = "single"
            elif i == 0: position = "top"
            elif i == count - 1: position = "bottom"
            
            cell = iOSTableCell(text, detail, position=position)
            sec_layout.addWidget(cell)
            
        self.layout.addWidget(section)
