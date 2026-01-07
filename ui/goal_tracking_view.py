"""
目标跟踪视图
展示学生的学习目标、进度、成就
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QProgressBar, QDialog,
    QFormLayout, QLineEdit, QTextEdit, QDateEdit, QComboBox,
    QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DatabaseManager
from services.goal_management_service import GoalManagementService
from database.models import Goal
from datetime import date


class GoalCard(QFrame):
    """目标卡片组件"""
    
    def __init__(self, goal: Goal, on_update=None):
        super().__init__()
        self.goal = goal
        self.on_update = on_update
        self._init_ui()
    
    def _init_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame:hover {
                border-color: #007AFF;
                background: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # 头部:目标类型和状态
        header = QHBoxLayout()
        type_label = QLabel(f"📌 {self.goal.goal_type}")
        type_label.setStyleSheet("color: #666; font-size: 12px;")
        header.addWidget(type_label)
        header.addStretch()
        
        status_label = QLabel(self.goal.status)
        if self.goal.status == "已完成":
            status_label.setStyleSheet("color: #34C759; font-weight: bold;")
        elif self.goal.status == "进行中":
            status_label.setStyleSheet("color: #007AFF; font-weight: bold;")
        else:
            status_label.setStyleSheet("color: #FF3B30;")
        header.addWidget(status_label)
        
        layout.addLayout(header)
        
        # 目标标题
        title = QLabel(self.goal.title)
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # 描述
        if self.goal.description:
            desc = QLabel(self.goal.description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666; font-size: 12px;")
            layout.addWidget(desc)
        
        # 进度条
        progress_layout = QHBoxLayout()
        progress_label = QLabel(f"进度: {self.goal.current_value:.0f} / {self.goal.target_value:.0f}")
        progress_layout.addWidget(progress_label)
        
        progress_bar = QProgressBar()
        progress_bar.setValue(int(self.goal.progress))
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007AFF, stop:1 #34C759);
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(progress_bar, 1)
        
        layout.addLayout(progress_layout)
        
        # 底部:截止日期
        footer = QHBoxLayout()
        if self.goal.deadline:
            days_left = (self.goal.deadline - date.today()).days
            deadline_text = f"⏰ 截止: {self.goal.deadline.strftime('%Y-%m-%d')}"
            if days_left < 0:
                deadline_text += f" (已超时)"
                color = "#FF3B30"
            elif days_left == 0:
                deadline_text += f" (今天)"
                color = "#FF9500"
            elif days_left <= 3:
                deadline_text += f" (还剩{days_left}天)"
                color = "#FF9500"
            else:
                deadline_text += f" (还剩{days_left}天)"
                color = "#34C759"
            
            deadline_label = QLabel(deadline_text)
            deadline_label.setStyleSheet(f"color: {color}; font-size: 12px;")
            footer.addWidget(deadline_label)
        
        footer.addStretch()
        layout.addLayout(footer)


class CreateGoalDialog(QDialog):
    """创建目标对话框"""
    
    def __init__(self, student_id: int, subjects: list, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.subjects = subjects
        self.goal = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("创建学习目标")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 表单
        form = QFormLayout()
        
        # 目标类型
        self.type_combo = QComboBox()
        self.type_combo.addItems(["成绩目标", "排名目标", "知识点目标", "学习习惯", "其他"])
        form.addRow("目标类型:", self.type_combo)
        
        # 标题
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例如:数学成绩提升到90分")
        form.addRow("* 目标标题:", self.title_edit)
        
        # 描述
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setPlaceholderText("详细描述你的目标...")
        form.addRow("描述:", self.desc_edit)
        
        # 目标值
        self.target_spin = QSpinBox()
        self.target_spin.setRange(0, 10000)
        self.target_spin.setValue(100)
        form.addRow("* 目标值:", self.target_spin)
        
        # 当前值
        self.current_spin = QSpinBox()
        self.current_spin.setRange(0, 10000)
        self.current_spin.setValue(0)
        form.addRow("当前值:", self.current_spin)
        
        # 关联科目
        self.subject_combo = QComboBox()
        self.subject_combo.addItem("不关联科目", None)
        for subj in self.subjects:
            self.subject_combo.addItem(subj.name, subj.id)
        form.addRow("关联科目:", self.subject_combo)
        
        # 截止日期
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDate(QDate.currentDate().addDays(30))
        form.addRow("* 截止日期:", self.deadline_edit)
        
        layout.addLayout(form)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("创建目标")
        create_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056CC;
            }
        """)
        create_btn.clicked.connect(self._create_goal)
        btn_layout.addWidget(create_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_goal(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请填写目标标题")
            return
        
        self.goal = Goal(
            student_id=self.student_id,
            goal_type=self.type_combo.currentText(),
            title=title,
            description=self.desc_edit.toPlainText().strip(),
            target_value=float(self.target_spin.value()),
            current_value=float(self.current_spin.value()),
            start_date=date.today(),
            deadline=self.deadline_edit.date().toPyDate(),
            status="进行中",
            progress=0.0,
            subject_id=self.subject_combo.currentData()
        )
        
        self.accept()


class GoalTrackingView(QWidget):
    """目标跟踪视图"""
    
    def __init__(self, db: DatabaseManager, goal_service: GoalManagementService):
        super().__init__()
        self.db = db
        self.goal_service = goal_service
        self.current_student_id = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题栏
        header = QHBoxLayout()
        title = QLabel("🎯 我的学习目标")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        # 学生选择
        header.addWidget(QLabel("学生:"))
        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(180)
        self.student_combo.currentIndexChanged.connect(self._on_student_changed)
        header.addWidget(self.student_combo)
        
        # 创建目标按钮
        create_btn = QPushButton("+ 创建新目标")
        create_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056CC;
            }
        """)
        create_btn.clicked.connect(self._create_goal)
        header.addWidget(create_btn)
        
        layout.addLayout(header)
        
        # 统计卡片区
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("总目标: 0")
        self.total_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(self.total_label)
        
        self.active_label = QLabel("进行中: 0")
        self.active_label.setStyleSheet("color: #007AFF; font-size: 14px;")
        stats_layout.addWidget(self.active_label)
        
        self.completed_label = QLabel("已完成: 0")
        self.completed_label.setStyleSheet("color: #34C759; font-size: 14px;")
        stats_layout.addWidget(self.completed_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 目标列表(滚动区)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        scroll_content = QWidget()
        self.goals_layout = QVBoxLayout(scroll_content)
        self.goals_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        
        # 成就墙区域
        achievements_section = QFrame()
        achievements_section.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        ach_layout = QVBoxLayout(achievements_section)
        
        ach_title = QLabel("🏆 成就墙")
        ach_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        ach_layout.addWidget(ach_title)
        
        self.achievements_label = QLabel("暂无成就，完成目标后会自动解锁!")
        self.achievements_label.setWordWrap(True)
        self.achievements_label.setStyleSheet("color: #666;")
        ach_layout.addWidget(self.achievements_label)
        
        layout.addWidget(achievements_section)
    
    def refresh(self):
        """刷新数据"""
        # 刷新学生列表
        self.student_combo.clear()
        self.student_combo.addItem("-- 请选择学生 --", None)
        for s in self.db.get_all_students():
            self.student_combo.addItem(f"{s.student_id} - {s.name}", s.id)
    
    def _on_student_changed(self):
        """学生选择变化"""
        student_id = self.student_combo.currentData()
        if not student_id:
            return
        
        self.current_student_id = student_id
        self._load_goals()
        self._load_achievements()
    
    def _load_goals(self):
        """加载目标列表"""
        if not self.current_student_id:
            return
        
        # 清空现有目标
        while self.goals_layout.count():
            item = self.goals_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 获取目标
        goals = self.goal_service.get_student_goals(self.current_student_id)
        
        # 统计
        total = len(goals)
        active = len([g for g in goals if g.status == "进行中"])
        completed = len([g for g in goals if g.status == "已完成"])
        
        self.total_label.setText(f"总目标: {total}")
        self.active_label.setText(f"进行中: {active}")
        self.completed_label.setText(f"已完成: {completed}")
        
        # 显示目标
        if not goals:
            no_goals = QLabel("📝 还没有设定目标，点击上方按钮创建你的第一个目标！")
            no_goals.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_goals.setStyleSheet("color: #999; padding: 50px; font-size: 14px;")
            self.goals_layout.addWidget(no_goals)
        else:
            for goal in goals:
                card = GoalCard(goal, on_update=self._load_goals)
                self.goals_layout.addWidget(card)
    
    def _load_achievements(self):
        """加载成就"""
        if not self.current_student_id:
            return
        
        achievements = self.goal_service.get_student_achievements(self.current_student_id, limit=5)
        
        if achievements:
            text = "  ".join([f"{a.icon} {a.title}" for a in achievements])
            self.achievements_label.setText(text)
        else:
            self.achievements_label.setText("暂无成就，完成目标后会自动解锁!")
    
    def _create_goal(self):
        """创建目标"""
        if not self.current_student_id:
            QMessageBox.warning(self, "提示", "请先选择学生")
            return
        
        subjects = self.db.get_all_subjects()
        dialog = CreateGoalDialog(self.current_student_id, subjects, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.goal:
            try:
                self.goal_service.create_goal(dialog.goal)
                QMessageBox.information(self, "成功", "目标创建成功！")
                self._load_goals()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建失败: {str(e)}")
