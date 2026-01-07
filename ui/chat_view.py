"""
AI对话视图 - 优化版
现代化聊天界面
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QPushButton, QTextEdit, QLineEdit, QFrame, QMessageBox,
    QDialog, QFormLayout, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor

from database.db_manager import DatabaseManager
from services.ai_service import AIService


class ChatWorker(QThread):
    """AI对话工作线程"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, ai_service, student_id, session_id, message):
        super().__init__()
        self.ai_service = ai_service
        self.student_id = student_id
        self.session_id = session_id
        self.message = message
    
    def run(self):
        try:
            response = self.ai_service.chat(self.student_id, self.session_id, self.message)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class ChatBubble(QFrame):
    """聊天气泡"""
    def __init__(self, message: str, is_user: bool = False):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # 角色标签
        role_layout = QHBoxLayout()
        if is_user:
            role_layout.addStretch()
        
        role = QLabel("👤 你" if is_user else "🤖 AI助手")
        role.setStyleSheet(f"color: #4a5568; font-size: 12px; margin-{'right' if is_user else 'left'}: 10px;")
        role_layout.addWidget(role)
        
        if not is_user:
            role_layout.addStretch()
        
        layout.addLayout(role_layout)
        
        # 消息内容
        msg_layout = QHBoxLayout()
        if is_user:
            msg_layout.addStretch()
        
        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(500)
        bubble.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if is_user:
            bubble.setStyleSheet("""
                QLabel {
                    background: white;
                    color: #2d3748;
                    padding: 15px 20px;
                    border-radius: 18px 18px 4px 18px;
                    font-size: 14px;
                    line-height: 1.5;
                    border: 2px solid #667eea;
                }
            """)
        else:
            bubble.setStyleSheet("""
                QLabel {
                    background: white;
                    color: #2d3748;
                    padding: 15px 20px;
                    border-radius: 18px 18px 18px 4px;
                    font-size: 14px;
                    line-height: 1.5;
                    border: 2px solid #e2e8f0;
                }
            """)
        
        msg_layout.addWidget(bubble)
        
        if not is_user:
            msg_layout.addStretch()
        
        layout.addLayout(msg_layout)


class ChatView(QWidget):
    """AI对话视图"""
    
    def __init__(self, db: DatabaseManager, ai_service: AIService):
        super().__init__()
        self.db = db
        self.ai_service = ai_service
        self.current_session_id = None
        self.worker = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题栏
        header = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        title = QLabel("🤖 AI职业规划顾问")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("通过对话了解你的兴趣和特点，提供专业选科和职业建议")
        subtitle.setStyleSheet("color: #718096; font-size: 13px;")
        title_layout.addWidget(subtitle)
        
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)
        
        # 工具栏
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        self._add_shadow(toolbar)
        
        toolbar_layout = QHBoxLayout(toolbar)
        
        toolbar_layout.addWidget(QLabel("选择学生:"))
        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(200)
        self.student_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
            }
        """)
        self.student_combo.currentIndexChanged.connect(self._on_student_changed)
        toolbar_layout.addWidget(self.student_combo)
        
        toolbar_layout.addStretch()
        
        self.new_btn = QPushButton("🆕 新对话")
        self.new_btn.setStyleSheet("""
            QPushButton {
                background: #48bb78;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background: #38a169; }
        """)
        self.new_btn.clicked.connect(self._start_new_session)
        toolbar_layout.addWidget(self.new_btn)
        
        self.report_btn = QPushButton("📋 生成报告")
        self.report_btn.setStyleSheet("""
            QPushButton {
                background: #ed8936;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover { background: #dd6b20; }
        """)
        self.report_btn.clicked.connect(self._generate_report)
        toolbar_layout.addWidget(self.report_btn)
        
        layout.addWidget(toolbar)
        
        # ═══ 3步引导式对话进度指示器 ═══
        journey_card = QFrame()
        journey_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 16px;
                padding: 5px;
            }
        """)
        self._add_shadow(journey_card)
        
        journey_inner = QWidget()
        journey_inner.setStyleSheet("background: transparent;")
        journey_layout = QVBoxLayout(journey_inner)
        journey_layout.setContentsMargins(20, 15, 20, 15)
        
        # 进度标题
        journey_title = QLabel("🎯 职业探索之旅")
        journey_title.setStyleSheet("color: white; font-size: 16px; font-weight: 600;")
        journey_layout.addWidget(journey_title)
        
        # 步骤指示器
        steps_layout = QHBoxLayout()
        steps_layout.setSpacing(0)
        
        self.step_labels = []
        step_info = [
            ("1", "兴趣探索", "聊聊你喜欢做什么"),
            ("2", "性格分析", "了解你的个性特点"),
            ("3", "规划建议", "生成专属职业报告")
        ]
        
        for i, (num, title, desc) in enumerate(step_info):
            step_widget = QWidget()
            step_widget.setStyleSheet("background: transparent;")
            step_layout_v = QVBoxLayout(step_widget)
            step_layout_v.setContentsMargins(10, 5, 10, 5)
            step_layout_v.setSpacing(2)
            
            # 步骤圆点
            step_num = QLabel(num)
            step_num.setFixedSize(28, 28)
            step_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
            step_num.setStyleSheet("""
                QLabel {
                    background: rgba(255,255,255,0.2);
                    color: rgba(255,255,255,0.7);
                    border-radius: 14px;
                    font-weight: 600;
                    font-size: 13px;
                }
            """)
            
            step_title = QLabel(title)
            step_title.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 13px; font-weight: 500;")
            step_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            step_layout_v.addWidget(step_num, 0, Qt.AlignmentFlag.AlignCenter)
            step_layout_v.addWidget(step_title)
            
            self.step_labels.append((step_num, step_title))
            steps_layout.addWidget(step_widget)
            
            # 连接线
            if i < 2:
                line = QFrame()
                line.setFixedHeight(2)
                line.setStyleSheet("background: rgba(255,255,255,0.3);")
                steps_layout.addWidget(line, 1)
        
        journey_layout.addLayout(steps_layout)
        
        # 当前进度提示
        self.progress_hint = QLabel("选择学生开始对话 →")
        self.progress_hint.setStyleSheet("color: rgba(255,255,255,0.7); font-size: 12px; margin-top: 5px;")
        self.progress_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        journey_layout.addWidget(self.progress_hint)
        
        journey_card_layout = QVBoxLayout(journey_card)
        journey_card_layout.setContentsMargins(0, 0, 0, 0)
        journey_card_layout.addWidget(journey_inner)
        
        layout.addWidget(journey_card)
        
        # 状态指示
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.status_label)
        self._update_status()
        
        # 聊天区域
        chat_card = QFrame()
        chat_card.setStyleSheet("""
            QFrame {
                background: #f7fafc;
                border-radius: 12px;
            }
        """)
        self._add_shadow(chat_card)
        
        chat_layout = QVBoxLayout(chat_card)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # 消息滚动区
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()
        
        self.scroll.setWidget(self.messages_widget)
        chat_layout.addWidget(self.scroll)
        
        # 输入区
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-top: 1px solid #e2e8f0;
                border-radius: 0 0 12px 12px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(20, 15, 20, 15)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入消息，与AI顾问交流...")
        self.message_input.setMinimumHeight(45)
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 22px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        self.message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("发送 →")
        self.send_btn.setMinimumHeight(45)
        self.send_btn.setMinimumWidth(100)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
            }
            QPushButton:disabled {
                background: #cbd5e0;
            }
        """)
        self.send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_btn)
        
        chat_layout.addWidget(input_frame)
        layout.addWidget(chat_card)
    
    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        widget.setGraphicsEffect(shadow)
    
    def refresh(self):
        self.student_combo.clear()
        self.student_combo.addItem("-- 请选择学生 --", None)
        for s in self.db.get_all_students():
            self.student_combo.addItem(f"{s.student_id} - {s.name}", s.id)
        self._update_status()
    
    def _update_status(self):
        if self.ai_service.is_available():
            self.status_label.setText("✅ AI智能助手已就绪")
            self.status_label.setStyleSheet("""
                QLabel {
                    background: #c6f6d5;
                    color: #22543d;
                    padding: 12px 20px;
                    border-radius: 8px;
                }
            """)
        else:
            self.status_label.setText("⚠️ AI服务未连接，请检查网络")
            self.status_label.setStyleSheet("""
                QLabel {
                    background: #fefcbf;
                    color: #744210;
                    padding: 12px 20px;
                    border-radius: 8px;
                }
            """)
    
    def _update_journey_progress(self, conversation_count: int = 0):
        """更新职业探索进度指示器"""
        # 计算当前阶段 (每4轮对话为一个阶段)
        if conversation_count == 0:
            current_step = 0
            hint = "选择学生开始对话 →"
        elif conversation_count < 4:
            current_step = 1
            hint = f"第1阶段: 聊聊你的兴趣爱好 ({conversation_count}/4轮)"
        elif conversation_count < 8:
            current_step = 2
            hint = f"第2阶段: 探索你的性格特点 ({conversation_count-4}/4轮)"
        else:
            current_step = 3
            hint = "✨ 已完成探索！可以生成报告了"
        
        # 更新步骤样式
        for i, (step_num, step_title) in enumerate(self.step_labels):
            if i + 1 < current_step:
                # 已完成
                step_num.setStyleSheet("""
                    QLabel {
                        background: white;
                        color: #667eea;
                        border-radius: 14px;
                        font-weight: 600;
                        font-size: 13px;
                    }
                """)
                step_num.setText("✓")
            elif i + 1 == current_step:
                # 当前
                step_num.setStyleSheet("""
                    QLabel {
                        background: white;
                        color: #667eea;
                        border-radius: 14px;
                        font-weight: 600;
                        font-size: 13px;
                    }
                """)
            else:
                # 未开始
                step_num.setStyleSheet("""
                    QLabel {
                        background: rgba(255,255,255,0.2);
                        color: rgba(255,255,255,0.7);
                        border-radius: 14px;
                        font-weight: 600;
                        font-size: 13px;
                    }
                """)
        
        self.progress_hint.setText(hint)
    
    def _on_student_changed(self):
        sid = self.student_combo.currentData()
        if sid:
            sessions = self.db.get_all_sessions(sid)
            if sessions:
                self.current_session_id = sessions[0]
                self._load_chat_history()
            else:
                self._start_new_session()
        else:
            self._clear_messages()
            self._update_journey_progress(0)  # 重置进度
    
    def _start_new_session(self):
        sid = self.student_combo.currentData()
        if not sid:
            QMessageBox.warning(self, "提示", "请先选择学生")
            return
        self.current_session_id = self.ai_service.start_session(sid)
        self._clear_messages()
        self._update_journey_progress(0)  # 新对话进度重置
        self._add_system_message("🎉 新对话开始！请随意和我聊聊，我会帮你发现自己的优势和兴趣方向。")
    
    def _clear_messages(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _load_chat_history(self):
        sid = self.student_combo.currentData()
        if not sid or not self.current_session_id:
            return
        self._clear_messages()
        history = self.db.get_conversation_history(sid, self.current_session_id)
        for c in history:
            self._add_bubble(c.message, c.role == "user")
        # 更新进度 (用户轮数为对话轮数)
        user_turns = sum(1 for c in history if c.role == "user")
        self._update_journey_progress(user_turns)
    
    def _add_bubble(self, message: str, is_user: bool):
        bubble = ChatBubble(message, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        ))
    
    def _add_system_message(self, message: str):
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: #718096;
                font-size: 13px;
                padding: 10px;
            }
        """)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, label)
    
    def _send_message(self):
        msg = self.message_input.text().strip()
        if not msg:
            return
        
        sid = self.student_combo.currentData()
        if not sid:
            QMessageBox.warning(self, "提示", "请先选择学生")
            return
        
        if not self.ai_service.is_available():
            QMessageBox.warning(self, "提示", "AI服务未连接")
            return
        
        if not self.current_session_id:
            self._start_new_session()
        
        self._add_bubble(msg, True)
        self.message_input.clear()
        self.send_btn.setEnabled(False)
        self.send_btn.setText("思考中...")
        
        self.worker = ChatWorker(self.ai_service, sid, self.current_session_id, msg)
        self.worker.finished.connect(self._on_response)
        self.worker.error.connect(self._on_error)
        self.worker.start()
    
    def _on_response(self, resp):
        self._add_bubble(resp, False)
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送 →")
        
        # 更新进度 (计算用户消息数)
        sid = self.student_combo.currentData()
        if sid and self.current_session_id:
            history = self.db.get_conversation_history(sid, self.current_session_id)
            user_turns = sum(1 for c in history if c.role == "user")
            self._update_journey_progress(user_turns)
    
    def _on_error(self, err):
        self._add_system_message(f"❌ 发生错误: {err}")
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送 →")
    
    def _generate_report(self):
        sid = self.student_combo.currentData()
        if not sid:
            QMessageBox.warning(self, "提示", "请先选择学生")
            return
        if not self.current_session_id:
            QMessageBox.warning(self, "提示", "请先进行对话")
            return
        
        self._add_system_message("📋 正在生成职业规划报告...")
        report = self.ai_service.generate_career_report(sid, self.current_session_id)
        if report:
            QMessageBox.information(self, "成功", "报告已生成！请到「规划报告」页面查看。")
        else:
            QMessageBox.warning(self, "失败", "报告生成失败，请重试")
