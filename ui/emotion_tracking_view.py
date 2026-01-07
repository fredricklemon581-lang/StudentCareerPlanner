"""
情绪跟踪视图
记录情绪日记、查看压力指数、获取心理疏导建议
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSlider, QTextEdit, QGroupBox,
    QDialog, QFormLayout, QLineEdit, QMessageBox, QGridLayout,
    QComboBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DatabaseManager
from services.emotion_tracking_service import EmotionTrackingService
from database.models import EmotionLog
from datetime import datetime, date

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class EmotionRecordDialog(QDialog):
    """情绪记录对话框"""
    
    def __init__(self, student_id: int, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.emotion_log = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("记录今日心情")
        self.setModal(True)
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        
        # 说明
        info = QLabel("📝 记录你今天的感受，帮助我们更好地了解你的状态")
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(info)
        
        # 滑块组
        self.mood_slider = self._create_slider_group("😊 心情", ["很差", "较差", "一般", "较好", "很好"], layout)
        self.stress_slider = self._create_slider_group("😰 压力", ["很轻松", "较轻松", "一般", "较大", "很大"], layout)
        self.energy_slider = self._create_slider_group("⚡ 精力", ["疲惫", "较累", "一般", "较好", "充沛"], layout)
        self.motivation_slider = self._create_slider_group("🎯 学习动力", ["很低", "较低", "一般", "较高", "很高"], layout)
        
        # 日记内容
        diary_label = QLabel("今日日记 (选填):")
        layout.addWidget(diary_label)
        
        self.diary_edit = QTextEdit()
        self.diary_edit.setPlaceholderText("记录今天发生的事情、你的感受、遇到的挑战...")
        self.diary_edit.setMaximumHeight(120)
        layout.addWidget(self.diary_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存记录")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self._save_record)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_slider_group(self, title: str, labels: list, parent_layout):
        """创建滑块组"""
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)
        
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setMinimum(1)
        slider.setMaximum(5)
        slider.setValue(3)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)
        
        labels_layout = QHBoxLayout()
        for label in labels:
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 11px; color: #666;")
            labels_layout.addWidget(lbl)
        
        group_layout.addWidget(slider)
        group_layout.addLayout(labels_layout)
        
        parent_layout.addWidget(group)
        return slider
    
    def _save_record(self):
        self.emotion_log = EmotionLog(
            student_id=self.student_id,
            log_date=date.today(),
            mood_score=self.mood_slider.value(),
            stress_level=self.stress_slider.value(),
            energy_level=self.energy_slider.value(),
            study_motivation=self.motivation_slider.value(),
            diary_content=self.diary_edit.toPlainText().strip(),
            tags=""
        )
        self.accept()


class EmotionTrackingView(QWidget):
    """情绪跟踪视图"""
    
    def __init__(self, db: DatabaseManager, emotion_service: EmotionTrackingService):
        super().__init__()
        self.db = db
        self.emotion_service = emotion_service
        self.current_student_id = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 标题栏
        header = QHBoxLayout()
        title = QLabel("💚 情绪健康中心")
        title.setFont(QFont("Microsoft YaHei",18, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        # 学生选择
        header.addWidget(QLabel("学生:"))
        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(180)
        self.student_combo.currentIndexChanged.connect(self._on_student_changed)
        header.addWidget(self.student_combo)
        
        # 记录按钮
        record_btn = QPushButton("📝 记录今日心情")
        record_btn.setStyleSheet("""
            QPushButton {
                background: #34C759;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #28A745;
            }
        """)
        record_btn.clicked.connect(self._record_emotion)
        header.addWidget(record_btn)
        
        layout.addLayout(header)
        
        # 压力指数仪表盘
        stress_panel = QFrame()
        stress_panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        stress_layout = QHBoxLayout(stress_panel)
        
        stress_left = QVBoxLayout()
        stress_title = QLabel("😰 压力指数")
        stress_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        stress_left.addWidget(stress_title)
        
        self.stress_value_label = QLabel("--")
        self.stress_value_label.setStyleSheet("color: white; font-size: 48px; font-weight: bold;")
        stress_left.addWidget(self.stress_value_label)
        
        self.stress_level_label = QLabel("暂无数据")
        self.stress_level_label.setStyleSheet("color: rgba(255,255,255,0.9); font-size: 14px;")
        stress_left.addWidget(self.stress_level_label)
        
        stress_layout.addLayout(stress_left)
        stress_layout.addStretch()
        
        self.stress_advice_label = QLabel("开始记录情绪以获取个性化建议")
        self.stress_advice_label.setWordWrap(True)
        self.stress_advice_label.setStyleSheet("color: rgba(255,255,255,0.95); font-size: 13px;")
        self.stress_advice_label.setMaximumWidth(300)
        stress_layout.addWidget(self.stress_advice_label)
        
        layout.addWidget(stress_panel)
        
        # 趋势图表
        chart_group = QGroupBox("📈 情绪趋势 (最近14天)")
        chart_layout = QVBoxLayout(chart_group)
        
        self.trend_canvas = FigureCanvas(Figure(figsize=(10, 4)))
        chart_layout.addWidget(self.trend_canvas)
        
        layout.addWidget(chart_group)
        
        # 最近日记
        diary_group = QGroupBox("📔 最近日记")
        diary_layout = QVBoxLayout(diary_group)
        
        diary_scroll = QScrollArea()
        diary_scroll.setWidgetResizable(True)
        diary_scroll.setMaximumHeight(200)
        
        self.diary_content = QWidget()
        self.diary_layout = QVBoxLayout(self.diary_content)
        self.diary_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        diary_scroll.setWidget(self.diary_content)
        
        diary_layout.addWidget(diary_scroll)
        layout.addWidget(diary_group)
    
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
        self._load_stress_index()
        self._load_emotion_trend()
        self._load_recent_diaries()
    
    def _load_stress_index(self):
        """加载压力指数"""
        if not self.current_student_id:
            return
        
        result = self.emotion_service.calculate_stress_index(self.current_student_id)
        
        stress_index = result['stress_index']
        self.stress_value_label.setText(f"{stress_index:.0f}")
        self.stress_level_label.setText(f"{result['level']} | 趋势: {result['trend']}")
        self.stress_advice_label.setText(result['recommendation'])
    
    def _load_emotion_trend(self):
        """加载情绪趋势图"""
        if not self.current_student_id:
            return
        
        trend = self.emotion_service.get_emotion_trend(self.current_student_id, days=14)
        
        if not trend['dates']:
            return
        
        self.trend_canvas.figure.clear()
        ax = self.trend_canvas.figure.add_subplot(111)
        
        x = range(len(trend['dates']))
        ax.plot(x, trend['mood_scores'], 'o-', label='心情', linewidth=2, markersize=6)
        ax.plot(x, trend['stress_levels'], 's-', label='压力', linewidth=2, markersize=6)
        ax.plot(x, trend['energy_levels'], '^-', label='精力', linewidth=2, markersize=6)
        ax.plot(x, trend['motivation_levels'], 'd-', label='动力', linewidth=2, markersize=6)
        
        ax.set_ylim(0, 6)
        ax.set_ylabel('评分')
        ax.set_title('情绪变化趋势', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # 设置x轴标签
        ax.set_xticks(x[::2])  # 每隔一天显示
        ax.set_xticklabels([d.split('-')[1:] for d in trend['dates'][::2]], rotation=45)
        
        self.trend_canvas.figure.tight_layout()
        self.trend_canvas.draw()
    
    def _load_recent_diaries(self):
        """加载最近日记"""
        if not self.current_student_id:
            return
        
        # 清空现有内容
        while self.diary_layout.count():
            item = self.diary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        logs = self.emotion_service.get_recent_emotions(self.current_student_id, days=7)
        
        if not logs:
            no_diary = QLabel("还没有日记记录，点击上方按钮开始记录吧！")
            no_diary.setStyleSheet("color: #999; padding: 20px;")
            no_diary.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.diary_layout.addWidget(no_diary)
            return
        
        for log in logs:
            if log.diary_content:
                diary_card = QFrame()
                diary_card.setStyleSheet("""
                    QFrame {
                        background: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 10px;
                        margin: 5px 0;
                    }
                """)
                card_layout = QVBoxLayout(diary_card)
                
                # 日期和分数
                header = QHBoxLayout()
                date_label = QLabel(f"📅 {log.log_date.strftime('%Y-%m-%d')}")
                date_label.setStyleSheet("font-weight: bold;")
                header.addWidget(date_label)
                
                scores = QLabel(f"心情:{log.mood_score} 压力:{log.stress_level}")
                scores.setStyleSheet("color: #666; font-size: 12px;")
                header.addWidget(scores)
                header.addStretch()
                
                card_layout.addLayout(header)
                
                # 日记内容
                content = QLabel(log.diary_content[:200] + ("..." if len(log.diary_content) > 200 else ""))
                content.setWordWrap(True)
                content.setStyleSheet("color: #333; margin-top: 5px;")
                card_layout.addWidget(content)
                
                self.diary_layout.addWidget(diary_card)
    
    def _record_emotion(self):
        """记录情绪"""
        if not self.current_student_id:
            QMessageBox.warning(self, "提示", "请先选择学生")
            return
        
        dialog = EmotionRecordDialog(self.current_student_id, self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.emotion_log:
            try:
                # 生成AI建议
                suggestions = self.emotion_service.generate_ai_suggestions(
                    self.current_student_id, dialog.emotion_log
                )
                dialog.emotion_log.ai_suggestions = suggestions
                
                # 保存
                self.emotion_service.log_emotion(dialog.emotion_log)
                
                QMessageBox.information(self, "成功", f"记录成功！\n\n💡 {suggestions}")
                
                # 刷新显示
                self._load_stress_index()
                self._load_emotion_trend()
                self._load_recent_diaries()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")


from PyQt6.QtWidgets import QComboBox
