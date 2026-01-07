"""
学生管理视图 - 优化版
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QDialog, QFormLayout, QComboBox,
    QMessageBox, QFileDialog, QHeaderView, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.db_manager import DatabaseManager
from database.models import Student
from utils.data_import import DataImporter
import config


class StudentView(QWidget):
    """学生管理视图"""
    
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.importer = DataImporter(db)
        self._init_ui()
        self.refresh()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 标题栏
        header = QHBoxLayout()
        
        title_layout = QVBoxLayout()
        title = QLabel("👨‍🎓 学生管理")
        title.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2d3748;")
        title_layout.addWidget(title)
        
        subtitle = QLabel("管理学生信息，支持批量导入")
        subtitle.setStyleSheet("color: #718096; font-size: 13px;")
        title_layout.addWidget(subtitle)
        
        header.addLayout(title_layout)
        header.addStretch()
        layout.addLayout(header)
        
        # 工具栏卡片
        toolbar_card = QFrame()
        toolbar_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        self._add_shadow(toolbar_card)
        
        toolbar = QHBoxLayout(toolbar_card)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 搜索学号或姓名...")
        self.search_input.setMinimumWidth(300)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        self.search_input.textChanged.connect(self._search)
        toolbar.addWidget(self.search_input)
        
        toolbar.addStretch()
        
        # 按钮组
        btn_style = """
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
        """
        
        self.add_btn = QPushButton("➕ 添加学生")
        self.add_btn.setStyleSheet(btn_style + """
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
            }
            QPushButton:hover { background: #5a67d8; }
        """)
        self.add_btn.clicked.connect(self._show_add_dialog)
        toolbar.addWidget(self.add_btn)
        
        self.import_btn = QPushButton("📥 导入Excel")
        self.import_btn.setStyleSheet(btn_style + """
            QPushButton {
                background: #48bb78;
                color: white;
                border: none;
            }
            QPushButton:hover { background: #38a169; }
        """)
        self.import_btn.clicked.connect(self._import_students)
        toolbar.addWidget(self.import_btn)
        
        self.template_btn = QPushButton("📄 下载模板")
        self.template_btn.setStyleSheet(btn_style + """
            QPushButton {
                background: white;
                color: #4a5568;
                border: 2px solid #e2e8f0;
            }
            QPushButton:hover { background: #f7fafc; border-color: #cbd5e0; }
        """)
        self.template_btn.clicked.connect(self._download_template)
        toolbar.addWidget(self.template_btn)
        
        layout.addWidget(toolbar_card)
        
        # 表格卡片
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
            }
        """)
        self._add_shadow(table_card)
        
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "学号", "姓名", "性别", "年级", "班级", "操作"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(6, 120)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget {
                border: none;
                border-radius: 12px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #667eea20;
                color: #2d3748;
            }
            QHeaderView::section {
                background-color: #f7fafc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #4a5568;
            }
        """)
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_card)
        
        # 统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #718096; font-size: 13px;")
        layout.addWidget(self.stats_label)
    
    def _add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 25))
        widget.setGraphicsEffect(shadow)
    
    def refresh(self):
        students = self.db.get_all_students()
        self._display_students(students)
    
    def _display_students(self, students):
        self.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(str(student.id)))
            self.table.setItem(row, 1, QTableWidgetItem(student.student_id))
            self.table.setItem(row, 2, QTableWidgetItem(student.name))
            self.table.setItem(row, 3, QTableWidgetItem(student.gender or ""))
            self.table.setItem(row, 4, QTableWidgetItem(student.grade or ""))
            self.table.setItem(row, 5, QTableWidgetItem(student.class_name or ""))
            
            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 2, 5, 2)
            
            del_btn = QPushButton("删除")
            del_btn.setStyleSheet("""
                QPushButton {
                    background: #fed7d7;
                    color: #c53030;
                    border: none;
                    padding: 5px 12px;
                    border-radius: 4px;
                    font-size: 12px;
                }
                QPushButton:hover { background: #feb2b2; }
            """)
            del_btn.clicked.connect(lambda _, s=student: self._delete_student(s))
            btn_layout.addWidget(del_btn)
            
            self.table.setCellWidget(row, 6, btn_widget)
        
        self.stats_label.setText(f"共 {len(students)} 名学生")
    
    def _search(self, keyword):
        if keyword:
            students = self.db.search_students(keyword)
        else:
            students = self.db.get_all_students()
        self._display_students(students)
    
    def _show_add_dialog(self):
        dialog = StudentDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()
    
    def _delete_student(self, student):
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除学生 {student.name} 吗？\n此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_student(student.id)
            self.refresh()
    
    def _import_students(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择Excel文件", "", "Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            success, errors = self.importer.import_students_from_excel(file_path)
            self.refresh()
            msg = f"成功导入 {success} 名学生"
            if errors:
                msg += f"\n\n以下行导入失败:\n" + "\n".join(errors[:5])
            QMessageBox.information(self, "导入结果", msg)
    
    def _download_template(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存模板", "学生导入模板.xlsx", "Excel文件 (*.xlsx)"
        )
        if file_path:
            if self.importer.generate_import_template('students', file_path):
                QMessageBox.information(self, "成功", f"模板已保存到:\n{file_path}")


class StudentDialog(QDialog):
    """学生编辑对话框"""
    
    def __init__(self, parent, db: DatabaseManager, student: Student = None):
        super().__init__(parent)
        self.db = db
        self.student = student
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("添加学生" if not self.student else "编辑学生")
        self.setMinimumWidth(450)
        self.setStyleSheet("""
            QDialog { background: white; }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #667eea;
            }
        """)
        
        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("如: 2024001")
        layout.addRow("学号 *", self.id_input)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("学生姓名")
        layout.addRow("姓名 *", self.name_input)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "男", "女"])
        layout.addRow("性别", self.gender_combo)
        
        self.grade_combo = QComboBox()
        self.grade_combo.addItems([""] + config.GRADES)
        layout.addRow("年级", self.grade_combo)
        
        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("如: 1班")
        layout.addRow("班级", self.class_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                background: white;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 24px;
                border: none;
                border-radius: 6px;
                background: #667eea;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover { background: #5a67d8; }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)
    
    def _save(self):
        sid = self.id_input.text().strip()
        name = self.name_input.text().strip()
        
        if not sid or not name:
            QMessageBox.warning(self, "提示", "请填写学号和姓名")
            return
        
        student = Student(
            student_id=sid,
            name=name,
            gender=self.gender_combo.currentText() or None,
            grade=self.grade_combo.currentText() or None,
            class_name=self.class_input.text().strip() or None
        )
        
        try:
            self.db.add_student(student)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
