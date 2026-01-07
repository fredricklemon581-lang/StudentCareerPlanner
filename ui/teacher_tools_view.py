# -*- coding: utf-8 -*-
"""
教师工具视图 - 题库管理 + 智能组卷
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit, QGroupBox, QSpinBox, QCheckBox,
    QMessageBox, QScrollArea, QFrame, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DatabaseManager
from services.weakness_analysis_service import WeaknessAnalysisService
from services.intelligent_exam_generator import IntelligentExamGenerator


class TeacherToolsView(QWidget):
    """教师工具综合视图"""
    
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.weakness_analyzer = WeaknessAnalysisService(db)
        self.exam_generator = IntelligentExamGenerator(db)
        
        self.current_student_id = None
        self.current_subject_id = None
        self.generated_questions = []
        self.exam_objects = {}  # 存储试卷对象
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("🎯 教师智能工具")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 标签页
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_question_bank_tab(), "📚 题库管理")
        tab_widget.addTab(self._create_exam_generator_tab(), "🤖 智能组卷")
        
        layout.addWidget(tab_widget)
    
    def _create_question_bank_tab(self):
        """创建题库管理标签页"""
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        
        # 左侧：试卷列表
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("📋 试卷列表"))
        
        # 试卷筛选
        exam_filter_layout = QHBoxLayout()
        exam_filter_layout.addWidget(QLabel("科目:"))
        self.exam_subject_combo = QComboBox()
        self.exam_subject_combo.currentIndexChanged.connect(self._load_exams)
        exam_filter_layout.addWidget(self.exam_subject_combo)
        left_layout.addLayout(exam_filter_layout)
        
        # 试卷列表
        self.exam_list = QTableWidget()
        self.exam_list.setColumnCount(2)
        self.exam_list.setHorizontalHeaderLabels(["试卷名称", "日期"])
        self.exam_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.exam_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.exam_list.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.exam_list.cellClicked.connect(self._on_exam_selected)
        left_layout.addWidget(self.exam_list)
        
        main_layout.addWidget(left_panel)
        
        # 右侧：题目列表
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 筛选条件
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("科目:"))
        self.qb_subject_combo = QComboBox()
        self.qb_subject_combo.setMinimumWidth(120)
        self.qb_subject_combo.currentIndexChanged.connect(self._on_subject_changed_qb)
        filter_layout.addWidget(self.qb_subject_combo)
        
        filter_layout.addWidget(QLabel("知识点:"))
        self.qb_kp_combo = QComboBox()
        self.qb_kp_combo.setMinimumWidth(150)
        filter_layout.addWidget(self.qb_kp_combo)
        
        filter_layout.addWidget(QLabel("题型:"))
        self.qb_type_combo = QComboBox()
        self.qb_type_combo.addItems(["全部", "选择题", "填空题", "解答题"])
        filter_layout.addWidget(self.qb_type_combo)
        
        search_btn = QPushButton("🔍 搜索")
        search_btn.clicked.connect(self._search_questions)
        filter_layout.addWidget(search_btn)
        
        filter_layout.addStretch()
        right_layout.addLayout(filter_layout)
        
        # 题目列表
        self.qb_table = QTableWidget()
        self.qb_table.setColumnCount(6)
        self.qb_table.setHorizontalHeaderLabels(
            ["题号", "题型", "难度", "分值", "知识点", "操作"]
        )
        self.qb_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.qb_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.qb_table)
        
        # 统计信息
        self.qb_stats_label = QLabel("题目总数: 0")
        self.qb_stats_label.setStyleSheet("color: #666; padding: 10px;")
        right_layout.addWidget(self.qb_stats_label)
        
        main_layout.addWidget(right_panel)
        
        return widget
    
    def _create_exam_generator_tab(self):
        """创建智能组卷标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 使用分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：设置面板
        left_panel = self._create_generator_settings()
        splitter.addWidget(left_panel)
        
        # 右侧：结果展示
        right_panel = self._create_generator_results()
        splitter.addWidget(right_panel)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter)
        
        return widget
    
    def _create_generator_settings(self):
        """创建组卷设置面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 学生选择
        group1 = QGroupBox("📋 基本设置")
        g1_layout = QVBoxLayout(group1)
        
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("学生:"))
        self.gen_student_combo = QComboBox()
        self.gen_student_combo.setMinimumWidth(150)
        self.gen_student_combo.currentIndexChanged.connect(self._on_student_selected)
        h1.addWidget(self.gen_student_combo)
        g1_layout.addLayout(h1)
        
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("科目:"))
        self.gen_subject_combo = QComboBox()
        self.gen_subject_combo.setMinimumWidth(150)
        h2.addWidget(self.gen_subject_combo)
        g1_layout.addLayout(h2)
        
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("总分:"))
        self.gen_total_score = QSpinBox()
        self.gen_total_score.setRange(50, 200)
        self.gen_total_score.setValue(100)
        self.gen_total_score.setSuffix(" 分")
        h3.addWidget(self.gen_total_score)
        h3.addStretch()
        g1_layout.addLayout(h3)
        
        layout.addWidget(group1)
        
        # 薄弱点分析
        group2 = QGroupBox("📊 薄弱点分析")
        g2_layout = QVBoxLayout(group2)
        
        self.weakness_text = QTextEdit()
        self.weakness_text.setReadOnly(True)
        self.weakness_text.setMaximumHeight(150)
        self.weakness_text.setPlaceholderText("选择学生后显示薄弱知识点...")
        g2_layout.addWidget(self.weakness_text)
        
        analyze_btn = QPushButton("🔍 重新分析")
        analyze_btn.clicked.connect(self._analyze_weaknesses)
        g2_layout.addWidget(analyze_btn)
        
        layout.addWidget(group2)
        
        # 组卷选项
        group3 = QGroupBox("⚙️ 组卷选项")
        g3_layout = QVBoxLayout(group3)
        
        self.focus_weakness_check = QCheckBox("重点考察薄弱点 (70%)")
        self.focus_weakness_check.setChecked(True)
        g3_layout.addWidget(self.focus_weakness_check)
        
        h4 = QHBoxLayout()
        h4.addWidget(QLabel("难度:"))
        self.gen_difficulty_combo = QComboBox()
        self.gen_difficulty_combo.addItems(["简单", "中等", "困难"])
        self.gen_difficulty_combo.setCurrentIndex(1)
        h4.addWidget(self.gen_difficulty_combo)
        g3_layout.addLayout(h4)
        
        layout.addWidget(group3)
        
        # ═══ 一键智能组卷大按钮 ═══
        self.generate_btn = QPushButton("🤖 AI 一键智能组卷")
        self.generate_btn.setMinimumHeight(60)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 18px 24px;
                border-radius: 16px;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4c51bf, stop:1 #553c9a);
            }
            QPushButton:disabled {
                background: #a0aec0;
            }
        """)
        self.generate_btn.clicked.connect(self._generate_exam)
        layout.addWidget(self.generate_btn)
        
        # 提示文字
        hint_label = QLabel("✨ 选择学生后，AI将自动分析并一键生成针对性试卷")
        hint_label.setStyleSheet("color: #718096; font-size: 12px; padding: 5px;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_generator_results(self):
        """创建组卷结果面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 统计信息
        self.gen_stats_label = QLabel("等待生成...")
        self.gen_stats_label.setStyleSheet("""
            background: #E3F2FD;
            padding: 15px;
            border-radius: 8px;
            font-size: 13px;
        """)
        layout.addWidget(self.gen_stats_label)
        
        # 题目列表
        self.gen_question_table = QTableWidget()
        self.gen_question_table.setColumnCount(7)
        self.gen_question_table.setHorizontalHeaderLabels(
            ["序号", "题型", "难度", "分值", "知识点", "是否薄弱点", "操作"]
        )
        self.gen_question_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.gen_question_table.setAlternatingRowColors(True)
        layout.addWidget(self.gen_question_table)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        export_word_btn = QPushButton("📄 导出Word")
        export_word_btn.clicked.connect(self._export_word)
        btn_layout.addWidget(export_word_btn)
        
        export_pdf_btn = QPushButton("📑 导出PDF")
        export_pdf_btn.clicked.connect(self._export_pdf)
        btn_layout.addWidget(export_pdf_btn)
        
        preview_btn = QPushButton("👁️ 预览试卷")
        preview_btn.clicked.connect(self._preview_exam)
        btn_layout.addWidget(preview_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return widget
    
    def refresh(self):
        """刷新数据"""
        # 刷新科目列表
        subjects = self.db.get_all_subjects()
        
        self.qb_subject_combo.clear()
        self.gen_subject_combo.clear()
        self.exam_subject_combo.clear()
        
        self.qb_subject_combo.addItem("全部", None)
        self.exam_subject_combo.addItem("全部", None)
        for subj in subjects:
            self.qb_subject_combo.addItem(subj.name, subj.id)
            self.gen_subject_combo.addItem(subj.name, subj.id)
            self.exam_subject_combo.addItem(subj.name, subj.id)
        
        # 初始化知识点下拉框
        self.qb_kp_combo.clear()
        self.qb_kp_combo.addItem("全部", None)
        
        # 刷新学生列表
        students = self.db.get_all_students()
        self.gen_student_combo.clear()
        self.gen_student_combo.addItem("-- 选择学生 --", None)
        for student in students:
            self.gen_student_combo.addItem(
                f"{student.student_id} - {student.name}",
                student.id
            )
        
        # 加载试卷列表
        self._load_exams()
    
    def _search_questions(self):
        """搜索题目"""
        filters = {}
        
        subject_id = self.qb_subject_combo.currentData()
        if subject_id:
            filters['subject_id'] = subject_id
        
        q_type = self.qb_type_combo.currentText()
        if q_type != "全部":
            filters['question_type'] = q_type
        
        questions = self.db.search_questions(filters)
        
        # 显示结果
        self.qb_table.setRowCount(len(questions))
        
        for i, q in enumerate(questions):
            self.qb_table.setItem(i, 0, QTableWidgetItem(str(q.id)))
            self.qb_table.setItem(i, 1, QTableWidgetItem(q.question_type))
            
            difficulty_str = "★" * int(q.difficulty * 5)
            self.qb_table.setItem(i, 2, QTableWidgetItem(difficulty_str))
            
            self.qb_table.setItem(i, 3, QTableWidgetItem(str(q.score)))
            
            # 获取知识点
            kps = self.db.get_question_knowledge_points(q.id)
            kp_names = ", ".join([kp.name for kp in kps[:2]])
            if len(kps) > 2:
                kp_names += f" +{len(kps)-2}个"
            self.qb_table.setItem(i, 4, QTableWidgetItem(kp_names))
            
            # 操作按钮
            view_btn = QPushButton("查看")
            view_btn.clicked.connect(lambda checked, q=q: self._view_question(q))
            self.qb_table.setCellWidget(i, 5, view_btn)
        
        self.qb_stats_label.setText(f"题目总数: {len(questions)}")
    
    def _load_exams(self):
        """加载试卷列表"""
        subject_id = self.exam_subject_combo.currentData()
        
        if subject_id:
            exams = self.db.get_exams_by_subject(subject_id)
        else:
            exams = self.db.get_all_exams()
        
        self.exam_list.setRowCount(len(exams))
        
        # 存储exam对象用于后续获取
        self.exam_objects = {}
        
        for i, exam in enumerate(exams):
            self.exam_list.setItem(i, 0, QTableWidgetItem(exam.name))
            exam_date = str(exam.exam_date) if exam.exam_date else ""
            self.exam_list.setItem(i, 1, QTableWidgetItem(exam_date))
            self.exam_objects[i] = exam
    
    def _on_exam_selected(self, row, col):
        """试卷被选中，显示该试卷的题目"""
        if row not in self.exam_objects:
            return
        
        selected_exam = self.exam_objects[row]
        
        # 显示该试卷科目的所有题目
        # 注意：当前数据库结构中exam和question没有直接关联
        # 这里按科目显示题目
        filters = {'subject_id': selected_exam.subject_id}
        questions = self.db.search_questions(filters)
        
        # 更新科目选择（同步）
        index = self.qb_subject_combo.findData(selected_exam.subject_id)
        if index >= 0:
            self.qb_subject_combo.setCurrentIndex(index)
        
        # 显示结果
        self.qb_table.setRowCount(len(questions))
        
        for i, q in enumerate(questions):
            self.qb_table.setItem(i, 0, QTableWidgetItem(str(q.id)))
            self.qb_table.setItem(i, 1, QTableWidgetItem(q.question_type))
            
            difficulty_str = "★" * int(q.difficulty * 5)
            self.qb_table.setItem(i, 2, QTableWidgetItem(difficulty_str))
            
            self.qb_table.setItem(i, 3, QTableWidgetItem(str(q.score)))
            
            # 获取知识点
            kps = self.db.get_question_knowledge_points(q.id)
            kp_names = ", ".join([kp.name for kp in kps[:2]])
            if len(kps) > 2:
                kp_names += f" +{len(kps)-2}个"
            self.qb_table.setItem(i, 4, QTableWidgetItem(kp_names))
            
            # 操作按钮
            view_btn = QPushButton("查看")
            view_btn.clicked.connect(lambda checked, q=q: self._view_question(q))
            self.qb_table.setCellWidget(i, 5, view_btn)
        
        self.qb_stats_label.setText(f"📋 {selected_exam.name} - 题目总数: {len(questions)}")
    
    def _on_subject_changed_qb(self):
        """科目变化时，更新知识点下拉框"""
        subject_id = self.qb_subject_combo.currentData()
        
        self.qb_kp_combo.clear()
        self.qb_kp_combo.addItem("全部", None)
        
        if subject_id:
            # 获取该科目的所有知识点
            kps = self.db.get_knowledge_points_by_subject(subject_id)
            for kp in kps:
                self.qb_kp_combo.addItem(kp.name, kp.id)
    
    
    def _on_student_selected(self):
        """学生选择变化"""
        student_id = self.gen_student_combo.currentData()
        if student_id:
            self.current_student_id = student_id
            self._analyze_weaknesses()
    
    def _analyze_weaknesses(self):
        """分析学生薄弱点"""
        if not self.current_student_id:
            return
        
        subject_id = self.gen_subject_combo.currentData()
        weaknesses = self.weakness_analyzer.analyze_student_weaknesses(
            self.current_student_id, subject_id
        )
        
        # 显示结果
        if weaknesses:
            text = "🔍 识别到以下薄弱知识点：\n\n"
            for i, weak in enumerate(weaknesses[:10], 1):
                mastery_pct = weak['mastery_rate'] * 100
                text += f"{i}. {weak['subject_name']} - {weak['knowledge_point_name']}\n"
                text += f"   掌握率: {mastery_pct:.1f}% (已练习{weak['total_attempts']}题)\n\n"
            
            self.weakness_text.setText(text)
        else:
            self.weakness_text.setText("✅ 该学生暂无明显薄弱点，或缺少答题数据。")
    
    def _generate_exam(self):
        """生成试卷"""
        student_id = self.gen_student_combo.currentData()
        subject_id = self.gen_subject_combo.currentData()
        
        if not student_id or not subject_id:
            QMessageBox.warning(self, "提示", "请选择学生和科目！")
            return
        
        total_score = self.gen_total_score.value()
        difficulty_map = {"简单": "easy", "中等": "medium", "困难": "hard"}
        difficulty = difficulty_map[self.gen_difficulty_combo.currentText()]
        focus_weakness = self.focus_weakness_check.isChecked()
        
        # 调用智能组卷引擎
        result = self.exam_generator.generate_targeted_exam(
            student_id=student_id,
            subject_id=subject_id,
            total_score=total_score,
            focus_on_weaknesses=focus_weakness,
            difficulty_level=difficulty
        )
        
        self.generated_questions = result['questions']
        
        # 显示统计
        stats_text = f"""
📊 组卷完成！

• 题目数量: {result['actual_count']} 题
• 实际总分: {result['total_score']} 分
• 平均难度: {result['difficulty_stats']['average']}
• 难度分布: 简单{result['difficulty_stats']['distribution']['简单']}题, 
            中等{result['difficulty_stats']['distribution']['中等']}题, 
            困难{result['difficulty_stats']['distribution']['困难']}题
• 薄弱点覆盖: {result['weakness_coverage']['covered_count']}/{result['weakness_coverage']['total_count']} 
              ({result['weakness_coverage']['coverage_rate']*100:.0f}%)

💡 建议: {'; '.join(result['recommendations']) if result['recommendations'] else '试卷质量良好'}
        """.strip()
        
        self.gen_stats_label.setText(stats_text)
        
        # 显示题目列表
        self._display_generated_questions(result)
        
        QMessageBox.information(self, "成功", f"已生成包含{len(self.generated_questions)}道题的试卷！")
    
    def _display_generated_questions(self, result):
        """显示生成的题目"""
        questions = result['questions']
        weak_kp_ids = set(w['knowledge_point_id'] for w in result['weaknesses_analyzed'])
        
        self.gen_question_table.setRowCount(len(questions))
        
        for i, q in enumerate(questions):
            self.gen_question_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.gen_question_table.setItem(i, 1, QTableWidgetItem(q.question_type))
            
            difficulty_str = "★" * int(q.difficulty * 5)
            self.gen_question_table.setItem(i, 2, QTableWidgetItem(difficulty_str))
            
            self.gen_question_table.setItem(i, 3, QTableWidgetItem(str(q.score)))
            
            # 知识点
            kps = self.db.get_question_knowledge_points(q.id)
            kp_names = ", ".join([kp.name for kp in kps[:2]])
            self.gen_question_table.setItem(i, 4, QTableWidgetItem(kp_names))
            
            # 是否薄弱点
            is_weak = any(kp.id in weak_kp_ids for kp in kps)
            weak_item = QTableWidgetItem("✓" if is_weak else "")
            if is_weak:
                weak_item.setBackground(QColor("#FFE69C"))
            self.gen_question_table.setItem(i, 5, weak_item)
            
            # 操作
            remove_btn = QPushButton("移除")
            remove_btn.clicked.connect(lambda checked, idx=i: self._remove_question(idx))
            self.gen_question_table.setCellWidget(i, 6, remove_btn)
    
    def _remove_question(self, index):
        """移除题目"""
        if 0 <= index < len(self.generated_questions):
            del self.generated_questions[index]
            self._refresh_generated_table()
    
    def _refresh_generated_table(self):
        """刷新生成的题目表"""
        # 简化处理，重新生成
        pass
    
    def _view_question(self, question):
        """查看题目详情"""
        msg = QMessageBox(self)
        msg.setWindowTitle("题目详情")
        msg.setText(f"题目内容: {question.content}\n\n答案: {question.answer}")
        msg.exec()
    
    def _export_word(self):
        """导出Word"""
        QMessageBox.information(self, "提示", "Word导出功能开发中...")
    
    def _export_pdf(self):
        """导出PDF"""
        QMessageBox.information(self, "提示", "PDF导出功能开发中...")
    
    def _preview_exam(self):
        """预览试卷"""
        if not self.generated_questions:
            QMessageBox.warning(self, "提示", "请先生成试卷！")
            return
        
        preview_text = "=" * 50 + "\n"
        preview_text += "试卷预览\n"
        preview_text += "=" * 50 + "\n\n"
        
        for i, q in enumerate(self.generated_questions, 1):
            preview_text += f"{i}. [{q.question_type}] {q.score}分\n"
            preview_text += f"   {q.content}\n\n"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("试卷预览")
        msg.setText(preview_text)
        msg.exec()
