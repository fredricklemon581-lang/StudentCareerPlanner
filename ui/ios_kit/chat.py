# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, 
                           QLabel, QScrollArea, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont

# Import backend services (Assuming these are available in path)
# In real usage, these would be passed in or imported from root
try:
    from services.ai_service import AIService
    from database.db_manager import DatabaseManager
    from ui.chat_view import ChatWorker # Reuse worker
except ImportError:
    # Mock for UI dev if not available
    class ChatWorker(QThread):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)
        def __init__(self, *args): super().__init__()
        def run(self): self.finished.emit("Mock AI Response: I am an iOS-style bot.")

class iOSChatBubble(QFrame):
    """iMessage风格气泡"""
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(400)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # iMessage Colors
        # User: #007AFF (Blue)
        # AI: #E9E9EB (Gray)
        
        bg_color = "#007AFF" if is_user else "#E9E9EB"
        text_color = "white" if is_user else "black"
        align = Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft
        
        bubble.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                padding: 10px 16px;
                border-radius: 18px;
                font-size: 15px;
                line-height: 1.4;
            }}
        """)
        
        wrapper = QHBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        if is_user:
            wrapper.addStretch()
            wrapper.addWidget(bubble)
        else:
            wrapper.addWidget(bubble)
            wrapper.addStretch()
            
        layout.addLayout(wrapper)

class iOSChatView(QWidget):
    """iOS风格对话视图"""
    def __init__(self, nav_controller=None, parent=None):
        super().__init__(parent)
        self.nav = nav_controller
        # Mock services for now, in real integration these come from main window
        self.db = None 
        self.ai_service = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Header is handled by Window Title usually, but we can add a sub-header or glass bar
        # For now, let's just have the chat area content
        
        # 2. Chat Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: white; border: none;")
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Hide scrollbar for clean look
        
        content = QWidget()
        content.setStyleSheet("background: white;")
        self.msg_layout = QVBoxLayout(content)
        self.msg_layout.setContentsMargins(20, 20, 20, 20)
        self.msg_layout.setSpacing(10)
        self.msg_layout.addStretch()
        
        # Welcome Msg
        self.msg_layout.addWidget(iOSChatBubble("你好！我是你的AI职业规划助手。\n我们可以聊聊你的兴趣，或者直接开始规划。", False))
        
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)
        
        # 3. Input Area (Bottom Bar)
        input_bar = QFrame()
        input_bar.setStyleSheet("""
            QFrame {
                background: #F9F9F9; /* SystemChromeMaterial */
                border-top: 1px solid rgba(0,0,0,0.1);
            }
        """)
        input_bar.setFixedHeight(80) # Increased height for touch target
        
        ib_layout = QHBoxLayout(input_bar)
        ib_layout.setContentsMargins(20, 10, 20, 20) # Bottom padding for safe area
        
        # Camera/Add Button (Mock)
        btn_add = QPushButton("+")
        btn_add.setFixedSize(36, 36)
        btn_add.setStyleSheet("""
            QPushButton {
                background: #E9E9EB; color: #007AFF; border-radius: 18px; font-size: 24px; border: none;
            }
        """)
        ib_layout.addWidget(btn_add)
        
        # Text Input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("iMessage")
        self.input_field.setFixedHeight(36)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E5E5EA;
                border-radius: 18px;
                padding: 0 16px;
                font-size: 16px;
                background: white;
            }
        """)
        self.input_field.returnPressed.connect(self.send_msg)
        ib_layout.addWidget(self.input_field)
        
        # Send Button
        self.btn_send = QPushButton("↑")
        self.btn_send.setFixedSize(32, 32)
        self.btn_send.setStyleSheet("""
            QPushButton {
                background: #007AFF; color: white; border-radius: 16px; font-weight: bold; border: none;
            }
        """)
        self.btn_send.clicked.connect(self.send_msg)
        ib_layout.addWidget(self.btn_send)
        
        layout.addWidget(input_bar)
        
    def send_msg(self):
        text = self.input_field.text().strip()
        if not text: return
        
        # User Bubble
        self.msg_layout.addWidget(iOSChatBubble(text, True))
        self.input_field.clear()
        
        # Auto Scroll
        QTimer.singleShot(100, self.scroll_to_bottom)
        
        # Mock Response
        QTimer.singleShot(1000, lambda: self.receive_msg("这是模拟回复。\n在Phase 3完成时，我们将接入真实的Claude API。"))
        
    def receive_msg(self, text):
        self.msg_layout.addWidget(iOSChatBubble(text, False))
        self.scroll_to_bottom()
        
    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())
