"""
试卷管理视图
提供试卷和题目的管理功能
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QDialog, QFormLayout, QComboBox,
    QMessageBox, QFileDialog, QHeaderView, QTextEdit, QDoubleSpinBox,
    QGroupBox, QSplitter, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database.db_manager import DatabaseManager
from database.models import Question, KnowledgePoint
from utils.data_import import DataImporter
import config


class ExamView(QWidget):
    """试卷管理视图"""
    
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.importer = DataImporter(db)
        self._init_ui()
        self.refresh()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("📋 试卷管理")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        # 学科筛选
        toolbar.addWidget(QLabel("学科:"))
        self.subject_combo = QComboBox()
        self.subject_combo.setMinimumWidth(150)
        self.subject_combo.currentIndexChanged.connect(self._on_subject_changed)
        toolbar.addWidget(self.subject_combo)
        
        toolbar.addStretch()
        
        # 按钮组
        self.add_btn = QPushButton("➕ 添加题目")
        self.add_btn.clicked.connect(self._show_add_dialog)
        toolbar.addWidget(self.add_btn)
        
        self.import_btn = QPushButton("📥 导入题库")
        self.import_btn.clicked.connect(self._import_questions)
        toolbar.addWidget(self.import_btn)
        
        self.template_btn = QPushButton("📄 下载模板")
        self.template_btn.clicked.connect(self._download_template)
        toolbar.addWidget(self.template_btn)
        
        layout.addLayout(toolbar)
        
        # 主垂直分割布局
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # ======= 上部分：考试记录表 =======
        exam_stats_group = QGroupBox("📅 考试记录 (含成绩统计)")
        exam_stats_layout = QVBoxLayout(exam_stats_group)
        
        self.exam_stats_table = QTableWidget()
        self.exam_stats_table.setColumnCount(5)
        self.exam_stats_table.setHorizontalHeaderLabels([
            "考试名称", "考试日期", "参与人数", "平均分", "满分"
        ])
        self.exam_stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.exam_stats_table.setAlternatingRowColors(True)
        self.exam_stats_table.setMaximumHeight(180)
        self.exam_stats_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background: #f7fafc;
                border: none;
                padding: 8px;
                font-weight: bold;
                color: #4a5568;
            }
        """)
        exam_stats_layout.addWidget(self.exam_stats_table)
        main_splitter.addWidget(exam_stats_group)
        
        # ======= 下部分：原有的知识点+题目 =======
        # 分割布局
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：知识点树
        kp_group = QGroupBox("知识点")
        kp_layout = QVBoxLayout(kp_group)
        self.kp_tree = QTreeWidget()
        self.kp_tree.setHeaderLabel("知识点")
        self.kp_tree.itemClicked.connect(self._on_kp_selected)
        kp_layout.addWidget(self.kp_tree)
        splitter.addWidget(kp_group)
        
        # 右侧：题目表格
        question_group = QGroupBox("题目列表")
        question_layout = QVBoxLayout(question_group)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "题型", "题目内容", "难度", "分值", "知识点"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)
        
        question_layout.addWidget(self.table)
        splitter.addWidget(question_group)
        
        splitter.setSizes([200, 600])
        main_splitter.addWidget(splitter)
        
        main_splitter.setSizes([200, 400])
        layout.addWidget(main_splitter)
        
        # 统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.stats_label)
    
    def refresh(self):
        """刷新数据"""
        # 刷新学科列表
        current_subject_id = None
        if self.subject_combo.currentData():
            current_subject_id = self.subject_combo.currentData()
        
        self.subject_combo.clear()
        self.subject_combo.addItem("全部学科", None)
        
        subjects = self.db.get_all_subjects()
        for subject in subjects:
            self.subject_combo.addItem(subject.name, subject.id)
        
        if current_subject_id:
            for i in range(self.subject_combo.count()):
                if self.subject_combo.itemData(i) == current_subject_id:
                    self.subject_combo.setCurrentIndex(i)
                    break
        
        self._on_subject_changed()
    
    def _on_subject_changed(self):
        """学科选择变化"""
        subject_id = self.subject_combo.currentData()
        
        # 更新考试统计表
        self._update_exam_stats(subject_id)
        
        # 更新知识点树
        self._update_kp_tree(subject_id)
        
        # 更新题目列表
        self._update_questions(subject_id)
    
    def _update_exam_stats(self, subject_id):
        """更新考试统计表"""
        exam_stats = self.db.get_exam_statistics(subject_id)
        
        self.exam_stats_table.setRowCount(len(exam_stats))
        
        for row, stat in enumerate(exam_stats):
            self.exam_stats_table.setItem(row, 0, QTableWidgetItem(stat['exam_name']))
            self.exam_stats_table.setItem(row, 1, QTableWidgetItem(stat['exam_date']))
            self.exam_stats_table.setItem(row, 2, QTableWidgetItem(str(stat['participant_count'])))
            
            # 平均分带颜色
            avg_item = QTableWidgetItem(f"{stat['average_score']}")
            if stat['avg_score_rate'] >= 80:
                from PyQt6.QtGui import QColor
                avg_item.setForeground(QColor("#22543d"))
            elif stat['avg_score_rate'] < 60:
                from PyQt6.QtGui import QColor
                avg_item.setForeground(QColor("#c53030"))
            self.exam_stats_table.setItem(row, 3, avg_item)
            
            self.exam_stats_table.setItem(row, 4, QTableWidgetItem(f"{stat['total_score']:.0f}"))
    
    def _update_kp_tree(self, subject_id):
        """更新知识点树"""
        self.kp_tree.clear()
        
        if not subject_id:
            return
        
        kps = self.db.get_knowledge_points_by_subject(subject_id)
        
        # 构建树结构
        kp_items = {}
        for kp in kps:
            item = QTreeWidgetItem([kp.name])
            item.setData(0, Qt.ItemDataRole.UserRole, kp.id)
            
            if kp.parent_id and kp.parent_id in kp_items:
                kp_items[kp.parent_id].addChild(item)
            else:
                self.kp_tree.addTopLevelItem(item)
            
            kp_items[kp.id] = item
        
        self.kp_tree.expandAll()
    
    def _update_questions(self, subject_id, kp_id=None):
        """更新题目列表"""
        if subject_id:
            questions = self.db.get_questions_by_subject(subject_id)
        else:
            questions = []
            for subject in self.db.get_all_subjects():
                questions.extend(self.db.get_questions_by_subject(subject.id))
        
        self.table.setRowCount(len(questions))
        
        for row, question in enumerate(questions):
            self.table.setItem(row, 0, QTableWidgetItem(str(question.id)))
            self.table.setItem(row, 1, QTableWidgetItem(question.question_type))
            
            # 截取题目内容
            content = question.content[:50] + "..." if len(question.content) > 50 else question.content
            self.table.setItem(row, 2, QTableWidgetItem(content))
            
            self.table.setItem(row, 3, QTableWidgetItem(f"{question.difficulty:.1f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{question.score:.0f}"))
            self.table.setItem(row, 5, QTableWidgetItem(""))  # TODO: 显示知识点
        
        self.stats_label.setText(f"共 {len(questions)} 道题目")
    
    def _on_kp_selected(self, item):
        """知识点选中"""
        kp_id = item.data(0, Qt.ItemDataRole.UserRole)
        subject_id = self.subject_combo.currentData()
        self._update_questions(subject_id, kp_id)
    
    def _show_add_dialog(self):
        """显示添加题目对话框"""
        dialog = QuestionDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
            QMessageBox.information(self, "成功", "题目添加成功！")
    
    def _import_questions(self):
        """导入题库"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "",
            "Excel文件 (*.xlsx *.xls)"
        )
        
        if file_path:
            success, errors = self.importer.import_questions_from_excel(file_path)
            
            self.refresh()
            
            msg = f"成功导入 {success} 道题目"
            if errors:
                msg += f"\n\n以下行导入失败:\n" + "\n".join(errors[:10])
            
            if errors:
                QMessageBox.warning(self, "导入结果", msg)
            else:
                QMessageBox.information(self, "导入成功", msg)
    
    def _download_template(self):
        """下载导入模板"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", "题库导入模板.xlsx",
            "Excel文件 (*.xlsx)"
        )
        
        if file_path:
            if self.importer.generate_import_template('questions', file_path):
                QMessageBox.information(self, "成功", f"模板已保存到:\n{file_path}")
            else:
                QMessageBox.critical(self, "错误", "模板生成失败")


class QuestionDialog(QDialog):
    """题目编辑对话框"""
    
    def __init__(self, parent, db: DatabaseManager, question: Question = None):
        super().__init__(parent)
        self.db = db
        self.question = question
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("添加题目")
        self.setMinimumSize(600, 500)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        # 学科
        self.subject_combo = QComboBox()
        subjects = self.db.get_all_subjects()
        for subject in subjects:
            self.subject_combo.addItem(subject.name, subject.id)
        layout.addRow("学科 *", self.subject_combo)
        
        # 题型
        self.type_combo = QComboBox()
        self.type_combo.addItems(config.QUESTION_TYPES)
        layout.addRow("题型 *", self.type_combo)
        
        # 题目内容
        self.content_edit = QTextEdit()
        self.content_edit.setMinimumHeight(100)
        self.content_edit.setPlaceholderText("请输入题目内容...")
        layout.addRow("题目内容 *", self.content_edit)
        
        # 标准答案
        self.answer_edit = QTextEdit()
        self.answer_edit.setMinimumHeight(60)
        layout.addRow("标准答案", self.answer_edit)
        
        # 解析
        self.analysis_edit = QTextEdit()
        self.analysis_edit.setMinimumHeight(60)
        layout.addRow("解析", self.analysis_edit)
        
        # 难度系数
        self.difficulty_spin = QDoubleSpinBox()
        self.difficulty_spin.setRange(0, 1)
        self.difficulty_spin.setSingleStep(0.1)
        self.difficulty_spin.setValue(0.5)
        layout.addRow("难度系数", self.difficulty_spin)
        
        # 分值
        self.score_spin = QDoubleSpinBox()
        self.score_spin.setRange(0, 100)
        self.score_spin.setValue(5)
        layout.addRow("分值", self.score_spin)
        
        # 知识点
        self.kp_input = QLineEdit()
        self.kp_input.setPlaceholderText("多个知识点用逗号分隔")
        layout.addRow("知识点", self.kp_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QTextEdit, QLineEdit, QComboBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton:default {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
            }
        """)
    
    def _save(self):
        """保存"""
        if not self.content_edit.toPlainText().strip():
            QMessageBox.warning(self, "提示", "请输入题目内容")
            return
        
        subject_id = self.subject_combo.currentData()
        
        question = Question(
            subject_id=subject_id,
            content=self.content_edit.toPlainText().strip(),
            answer=self.answer_edit.toPlainText().strip(),
            analysis=self.analysis_edit.toPlainText().strip(),
            question_type=self.type_combo.currentText(),
            difficulty=self.difficulty_spin.value(),
            score=self.score_spin.value()
        )
        
        question_id = self.db.add_question(question)
        
        # 处理知识点
        kp_text = self.kp_input.text().strip()
        if kp_text:
            for kp_name in kp_text.split(','):
                kp_name = kp_name.strip()
                if kp_name:
                    # 查找或创建知识点
                    kps = self.db.get_knowledge_points_by_subject(subject_id)
                    kp_id = None
                    for kp in kps:
                        if kp.name == kp_name:
                            kp_id = kp.id
                            break
                    
                    if not kp_id:
                        kp = KnowledgePoint(
                            subject_id=subject_id,
                            name=kp_name,
                            level=1
                        )
                        kp_id = self.db.add_knowledge_point(kp)
                    
                    self.db.link_question_to_knowledge(question_id, kp_id)
        
        self.accept()
