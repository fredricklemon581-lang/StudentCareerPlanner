"""
数据分析视图 - 全新重构版
现代化设计 + 智能洞察 + 交互式图表
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel,
    QPushButton, QFrame, QScrollArea, QGroupBox, QTextEdit,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QGridLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 配置matplotlib中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

from database.db_manager import DatabaseManager
from services.analysis_service import AnalysisService


class ScoreCard(QFrame):
    """现代化统计卡片 - 简化版确保文字可见"""
    
    def __init__(self, title: str, value: str, subtitle: str = "", color: str = "#007AFF"):
        super().__init__()
        self.setFixedHeight(120)
        
        # 简化样式 - 只设置背景
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self._darken_color(color)});
                border-radius: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # 标题 - 使用最简单的方式
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Arial", 10))
        self.title_label.setStyleSheet("color: #FFFFFF; background: none; border: none;")
        layout.addWidget(self.title_label)
        
        # 数值 - 大号粗体
        self.value_label = QLabel(value)
        font = QFont("Arial", 32)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet("color: #FFFFFF; background: none; border: none;")
        layout.addWidget(self.value_label)
        
        # 副标题
        self.sub_label = None
        if subtitle:
            self.sub_label = QLabel(subtitle)
            self.sub_label.setFont(QFont("Arial", 9))
            self.sub_label.setStyleSheet("color: #EEEEEE; background: none; border: none;")
            layout.addWidget(self.sub_label)
        
        layout.addStretch()
    
    def update_value(self, value: str, subtitle: str = None):
        """更新卡片数值"""
        # 直接设置文本
        self.value_label.setText(value)
        self.value_label.setVisible(True)  # 确保可见
        
        if subtitle:
            if self.sub_label is None:
                # 创建新的副标题标签
                self.sub_label = QLabel(subtitle)
                self.sub_label.setFont(QFont("Arial", 9))
                self.sub_label.setStyleSheet("color: #EEEEEE; background: none; border: none;")
                self.layout().insertWidget(2, self.sub_label)
            else:
                self.sub_label.setText(subtitle)
            self.sub_label.setVisible(True)
        
        # 强制重绘
        self.update()
    
    def _darken_color(self, hex_color: str) -> str:
        """加深颜色"""
        c = hex_color.lstrip('#')
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        r, g, b = int(r * 0.7), int(g * 0.7), int(b * 0.7)
        return f"#{r:02x}{g:02x}{b:02x}"


class InsightCard(QFrame):
    """智能洞察卡片"""
    
    def __init__(self, insight: dict):
        super().__init__()
        self._setup_ui(insight)
    
    def _setup_ui(self, insight: dict):
        # 根据类型设置颜色
        colors = {
            'warning': ('#FFF3CD', '#856404', '#FFE69C'),
            'success': ('#D4EDDA', '#155724', '#C3E6CB'),
            'info': ('#CCE5FF', '#004085', '#B8DAFF')
        }
        bg, text, border = colors.get(insight['type'], colors['info'])
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 2px solid {border};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)
        
        # 标题
        title = QLabel(insight['title'])
        title.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {text};")
        layout.addWidget(title)
        
        # 内容
        content = QLabel(insight['content'])
        content.setWordWrap(True)
        content.setStyleSheet(f"color: {text};")
        layout.addWidget(content)


class AnalysisView(QWidget):
    """数据分析视图 - 重构版"""
    
    def __init__(self, db: DatabaseManager, analysis_service: AnalysisService):
        super().__init__()
        self.db = db
        self.analysis = analysis_service
        self.current_student_id = None
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ========== 顶部标题栏 ==========
        header = QHBoxLayout()
        
        title = QLabel("📊 智能数据分析中心")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        # 学生选择
        header.addWidget(QLabel("👤 学生:"))
        self.student_combo = QComboBox()
        self.student_combo.setMinimumWidth(200)
        self.student_combo.currentIndexChanged.connect(self._on_student_changed)
        header.addWidget(self.student_combo)
        
        # 刷新按钮
        refresh_btn = QPushButton("🔄 刷新分析")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #0056CC;
            }
        """)
        refresh_btn.clicked.connect(self._analyze)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # ========== 核心指标卡片区 ==========
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        self.avg_score_card = ScoreCard("📈 平均得分率", "--", "综合表现", "#007AFF")
        self.trend_card = ScoreCard("📊 整体趋势", "--", "进步情况", "#34C759")
        self.rank_card = ScoreCard("🏆 班级排名", "--", "相对位置", "#FF9500")
        self.rating_card = ScoreCard("⭐ 综合评级", "--", "多维评估", "#AF52DE")
        
        cards_layout.addWidget(self.avg_score_card)
        cards_layout.addWidget(self.trend_card)
        cards_layout.addWidget(self.rank_card)
        cards_layout.addWidget(self.rating_card)
        
        layout.addLayout(cards_layout)
        
        # ========== 主内容区 - 标签页 ==========
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E5E5EA;
                border-radius: 12px;
                background: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 4px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background: #007AFF;
                color: white;
                border-radius: 6px 6px 0 0;
            }
        """)
        
        # 标签页
        self.main_tabs.addTab(self._create_insights_tab(), "🎯 智能洞察")
        self.main_tabs.addTab(self._create_overview_tab(), "📊 综合概览")
        self.main_tabs.addTab(self._create_prediction_tab(), "🔮 成绩预测")
        self.main_tabs.addTab(self._create_comparison_tab(), "👥 同伴对比")
        self.main_tabs.addTab(self._create_correlation_tab(), "🔗 学科关联")
        
        layout.addWidget(self.main_tabs)
    
    def _create_insights_tab(self):
        """创建智能洞察标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("🎯 AI智能发现")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("系统自动分析您的学习数据，发现关键洞察和改进机会")
        desc.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # 洞察卡片容器
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        self.insights_container = QWidget()
        self.insights_layout = QVBoxLayout(self.insights_container)
        self.insights_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.insights_layout.setSpacing(12)
        
        scroll.setWidget(self.insights_container)
        layout.addWidget(scroll)
        
        return widget
    
    def _create_overview_tab(self):
        """创建综合概览标签页"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 左侧：雷达图
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        radar_title = QLabel("各科成绩雷达图")
        radar_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        left_layout.addWidget(radar_title)
        
        self.radar_canvas = FigureCanvas(Figure(figsize=(6, 6)))
        left_layout.addWidget(self.radar_canvas)
        
        layout.addWidget(left_widget, 1)
        
        # 右侧：多维度评分
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        score_title = QLabel("多维度能力评估")
        score_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        right_layout.addWidget(score_title)
        
        self.dimension_canvas = FigureCanvas(Figure(figsize=(5, 5)))
        right_layout.addWidget(self.dimension_canvas)
        
        # 评分详情
        self.score_details = QTextEdit()
        self.score_details.setReadOnly(True)
        self.score_details.setMaximumHeight(150)
        self.score_details.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.score_details)
        
        layout.addWidget(right_widget, 1)
        
        return widget
    
    def _create_prediction_tab(self):
        """创建成绩预测标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 科目选择
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("选择科目:"))
        
        self.prediction_subject_combo = QComboBox()
        self.prediction_subject_combo.setMinimumWidth(150)
        self.prediction_subject_combo.currentIndexChanged.connect(self._update_prediction)
        filter_layout.addWidget(self.prediction_subject_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # 预测结果区 - 固定高度
        result_frame = QFrame()
        result_frame.setFixedHeight(180)  # 固定高度
        result_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 16px;
                padding: 20px;
            }
        """)
        result_layout = QVBoxLayout(result_frame)
        result_layout.setSpacing(8)
        
        self.prediction_title = QLabel("🔮 下次考试分数预测")
        self.prediction_title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        result_layout.addWidget(self.prediction_title)
        
        self.prediction_value = QLabel("--")
        self.prediction_value.setStyleSheet("color: white; font-size: 42px; font-weight: bold;")
        result_layout.addWidget(self.prediction_value)
        
        info_layout = QHBoxLayout()
        self.prediction_range = QLabel("置信区间: --")
        self.prediction_range.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 12px;")
        info_layout.addWidget(self.prediction_range)
        
        self.prediction_trend = QLabel("趋势: --")
        self.prediction_trend.setStyleSheet("color: rgba(255,255,255,0.85); font-size: 12px;")
        info_layout.addWidget(self.prediction_trend)
        info_layout.addStretch()
        result_layout.addLayout(info_layout)
        
        self.prediction_warning = QLabel("")
        self.prediction_warning.setStyleSheet("color: #FFE69C; font-weight: bold;")
        self.prediction_warning.setWordWrap(True)
        result_layout.addWidget(self.prediction_warning)
        
        layout.addWidget(result_frame)
        
        # 趋势图 - 使用stretch让它占据剩余空间
        self.prediction_canvas = FigureCanvas(Figure(figsize=(10, 5)))
        layout.addWidget(self.prediction_canvas, 1)  # stretch factor = 1
        
        return widget
    
    def _create_comparison_tab(self):
        """创建同伴对比标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 班级对比概览
        overview = QLabel("📊 班级对比分析")
        overview.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        layout.addWidget(overview)
        
        self.comparison_summary = QLabel("选择学生后显示班级对比数据")
        self.comparison_summary.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(self.comparison_summary)
        
        # 排名表格
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(5)
        self.ranking_table.setHorizontalHeaderLabels(["科目", "排名", "百分位", "得分率", "比班均"])
        self.ranking_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ranking_table.setAlternatingRowColors(True)
        self.ranking_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E5E5EA;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        layout.addWidget(self.ranking_table)
        
        return widget
    
    def _create_correlation_tab(self):
        """创建学科关联标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🔗 学科相关性分析")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        desc = QLabel("发现不同学科之间的成绩关联性，帮助优化学习策略")
        desc.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc)
        
        # 相关性热力图
        self.correlation_canvas = FigureCanvas(Figure(figsize=(8, 6)))
        layout.addWidget(self.correlation_canvas)
        
        # 强相关发现
        self.correlation_findings = QTextEdit()
        self.correlation_findings.setReadOnly(True)
        self.correlation_findings.setMaximumHeight(120)
        self.correlation_findings.setStyleSheet("""
            QTextEdit {
                background: #E3F2FD;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.correlation_findings)
        
        return widget
    
    def refresh(self):
        """刷新数据"""
        self.student_combo.clear()
        self.student_combo.addItem("-- 请选择学生 --", None)
        
        for student in self.db.get_all_students():
            self.student_combo.addItem(f"{student.student_id} - {student.name}", student.id)
        
        # 刷新科目列表
        self.prediction_subject_combo.clear()
        for subj in self.db.get_all_subjects():
            self.prediction_subject_combo.addItem(subj.name, subj.id)
    
    def _on_student_changed(self):
        """学生选择变化 - 自动触发分析"""
        student_id = self.student_combo.currentData()
        if student_id:
            self.current_student_id = student_id
            # 立即执行分析
            self._analyze()
    
    def _analyze(self):
        """执行分析"""
        if not self.current_student_id:
            return
        
        self._update_cards()
        self._update_insights()
        self._update_overview()
        self._update_prediction()
        self._update_comparison()
        self._update_correlation()
    
    def _update_cards(self):
        """更新顶部卡片"""
        if not self.current_student_id:
            return
        
        try:
            # 获取综合评分
            scores = self.analysis.calculate_comprehensive_scores(self.current_student_id)
            
            # 更新卡片1: 平均得分率
            self.avg_score_card.update_value(
                f"{scores['mastery_score']:.0f}%",
                "掌握度评分"
            )
            
            # 获取报告
            report = self.analysis.analyze_student(self.current_student_id)
            if report:
                # 更新卡片2: 整体趋势
                trend = report.potential_analysis.overall_trend
                growth = report.potential_analysis.growth_rate
                self.trend_card.update_value(trend, f"增长率 {growth:.1f}%")
            
            # 获取排名
            comparison = self.analysis.compare_with_peers(self.current_student_id)
            if 'subject_rankings' in comparison and comparison['subject_rankings']:
                avg_rank = np.mean([r['rank'] for r in comparison['subject_rankings']])
                # 更新卡片3: 班级排名
                self.rank_card.update_value(
                    f"第{avg_rank:.0f}名",
                    f"班级共{comparison['class_size']}人"
                )
            else:
                self.rank_card.update_value("暂无", "需要班级数据")
            
            # 更新卡片4: 综合评级
            self.rating_card.update_value(scores['overall_rating'], "五维综合")
            
        except Exception as e:
            print(f"更新卡片时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_insights(self):
        """更新智能洞察"""
        if not self.current_student_id:
            return
        
        # 清空现有洞察
        while self.insights_layout.count():
            item = self.insights_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 获取洞察
        insights = self.analysis.generate_smart_insights(self.current_student_id)
        
        if not insights:
            no_insight = QLabel("暂无洞察，请录入更多成绩数据")
            no_insight.setStyleSheet("color: #999; padding: 30px;")
            no_insight.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.insights_layout.addWidget(no_insight)
        else:
            for insight in insights:
                card = InsightCard(insight)
                self.insights_layout.addWidget(card)
    
    def _update_overview(self):
        """更新综合概览"""
        if not self.current_student_id:
            return
        
        # 雷达图
        comparison = self.analysis.get_all_subjects_comparison(self.current_student_id)
        
        if comparison['subjects']:
            self.radar_canvas.figure.clear()
            ax = self.radar_canvas.figure.add_subplot(111, polar=True)
            
            # 准备数据
            subjects = comparison['subjects']
            scores = comparison['scores']
            
            # 计算角度
            angles = np.linspace(0, 2 * np.pi, len(subjects), endpoint=False).tolist()
            scores_plot = scores + [scores[0]]  # 闭合
            angles += angles[:1]
            
            # 绘制
            ax.fill(angles, scores_plot, alpha=0.25, color='#007AFF')
            ax.plot(angles, scores_plot, 'o-', linewidth=2, color='#007AFF', markersize=8)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(subjects, fontsize=10)
            ax.set_ylim(0, 100)
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.grid(True, alpha=0.3)
            
            self.radar_canvas.figure.tight_layout()
            self.radar_canvas.draw()
        
        # 多维度评分图
        scores = self.analysis.calculate_comprehensive_scores(self.current_student_id)
        
        self.dimension_canvas.figure.clear()
        ax = self.dimension_canvas.figure.add_subplot(111)
        
        dimensions = ['掌握度', '态度', '稳定性', '潜力', '均衡度']
        values = [
            scores['mastery_score'],
            scores['attitude_score'],
            scores['stability_score'],
            scores['potential_score'],
            scores['balance_score']
        ]
        
        colors = ['#007AFF', '#34C759', '#FF9500', '#AF52DE', '#FF2D55']
        bars = ax.barh(dimensions, values, color=colors, height=0.6)
        
        ax.set_xlim(0, 105)
        ax.set_xlabel('评分', fontsize=11)
        ax.tick_params(axis='y', labelsize=10)
        
        for bar, val in zip(bars, values):
            ax.text(val + 2, bar.get_y() + bar.get_height()/2, 
                   f'{val:.0f}', va='center', fontsize=10, fontweight='bold')
        
        ax.grid(axis='x', alpha=0.3)
        self.dimension_canvas.figure.tight_layout()
        self.dimension_canvas.draw()
        
        # 评分详情
        self.score_details.setFont(QFont("Microsoft YaHei", 10))
        self.score_details.setText(f"""
📊 综合评级: {scores['overall_rating']}

• 学科掌握度: {scores['mastery_score']:.0f}/100
• 学习态度: {scores['attitude_score']:.0f}/100  
• 成绩稳定性: {scores['stability_score']:.0f}/100
• 学习潜力: {scores['potential_score']:.0f}/100
• 学科均衡度: {scores['balance_score']:.0f}/100
        """.strip())
    
    def _update_prediction(self):
        """更新预测"""
        if not self.current_student_id:
            return
        
        subject_id = self.prediction_subject_combo.currentData()
        if not subject_id:
            # 默认选择第一个科目
            if self.prediction_subject_combo.count() > 0:
                self.prediction_subject_combo.setCurrentIndex(0)
                subject_id = self.prediction_subject_combo.itemData(0)
            else:
                return
        
        # 获取预测
        prediction = self.analysis.predict_next_score(self.current_student_id, subject_id)
        
        if prediction['predicted_score']:
            self.prediction_value.setText(f"{prediction['predicted_score']:.1f}分")
            self.prediction_range.setText(
                f"置信区间: {prediction['confidence_interval'][0]:.1f} - {prediction['confidence_interval'][1]:.1f}分"
            )
            self.prediction_trend.setText(f"趋势: {prediction['trend_strength']}")
            
            if prediction['warning']:
                self.prediction_warning.setText(prediction['warning'])
            else:
                self.prediction_warning.setText("")
        else:
            self.prediction_value.setText("数据不足")
            self.prediction_range.setText("需要至少2次考试成绩")
            self.prediction_trend.setText("")
            self.prediction_warning.setText("")
        
        # 绘制趋势图
        trend_data = self.analysis.get_subject_trend_data(self.current_student_id, subject_id)
        
        self.prediction_canvas.figure.clear()
        ax = self.prediction_canvas.figure.add_subplot(111)
        
        if trend_data['scores']:
            x = range(len(trend_data['scores']))
            ax.plot(x, trend_data['scores'], 'o-', linewidth=2.5, markersize=8, 
                   color='#007AFF', label='实际成绩')
            
            # 添加预测点
            if prediction['predicted_score']:
                ax.scatter([len(trend_data['scores'])], [prediction['predicted_score']], 
                          color='#FF9500', s=150, marker='*', zorder=5, label='预测分数')
                
                # 置信区间
                ax.fill_between(
                    [len(trend_data['scores'])-0.3, len(trend_data['scores'])+0.3],
                    [prediction['confidence_interval'][0], prediction['confidence_interval'][0]],
                    [prediction['confidence_interval'][1], prediction['confidence_interval'][1]],
                    alpha=0.3, color='#FF9500'
                )
            
            ax.set_ylabel('分数', fontsize=11)
            ax.set_xlabel('考试次数', fontsize=11)
            ax.set_title('成绩趋势与预测', fontsize=12, pad=10)
            ax.legend(fontsize=10, loc='best')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.tick_params(labelsize=10)
        
        self.prediction_canvas.figure.tight_layout(pad=1.5)
        self.prediction_canvas.draw()
    
    def _update_comparison(self):
        """更新同伴对比"""
        if not self.current_student_id:
            return
        
        comparison = self.analysis.compare_with_peers(self.current_student_id)
        
        if 'error' in comparison:
            self.comparison_summary.setText(comparison['error'])
            return
        
        # 更新概览
        self.comparison_summary.setText(
            f"班级人数: {comparison['class_size']}人 | "
            f"综合表现: 比班级平均 {'+' if comparison['vs_class_avg'] >= 0 else ''}{comparison['vs_class_avg']:.1f}%"
        )
        
        # 更新表格
        rankings = comparison.get('subject_rankings', [])
        self.ranking_table.setRowCount(len(rankings))
        
        for i, r in enumerate(rankings):
            self.ranking_table.setItem(i, 0, QTableWidgetItem(r['subject']))
            self.ranking_table.setItem(i, 1, QTableWidgetItem(f"{r['rank']}/{r['total']}"))
            self.ranking_table.setItem(i, 2, QTableWidgetItem(f"前{100-r['percentile']:.0f}%"))
            self.ranking_table.setItem(i, 3, QTableWidgetItem(f"{r['score_rate']:.1f}%"))
            
            vs_avg = r['vs_avg']
            vs_text = f"+{vs_avg:.1f}%" if vs_avg >= 0 else f"{vs_avg:.1f}%"
            item = QTableWidgetItem(vs_text)
            item.setForeground(QColor('#34C759' if vs_avg >= 0 else '#FF3B30'))
            self.ranking_table.setItem(i, 4, item)
    
    def _update_correlation(self):
        """更新学科关联"""
        if not self.current_student_id:
            return
        
        correlation = self.analysis.calculate_subject_correlation(self.current_student_id)
        
        if not correlation['subjects']:
            self.correlation_findings.setText("数据不足，无法计算学科相关性")
            return
        
        # 绘制热力图
        self.correlation_canvas.figure.clear()
        ax = self.correlation_canvas.figure.add_subplot(111)
        
        matrix = np.array(correlation['matrix'])
        subjects = correlation['subjects']
        
        im = ax.imshow(matrix, cmap='RdYlBu_r', vmin=-1, vmax=1, aspect='auto')
        
        # 添加标签
        ax.set_xticks(range(len(subjects)))
        ax.set_yticks(range(len(subjects)))
        ax.set_xticklabels(subjects, rotation=45, ha='right', fontsize=10)
        ax.set_yticklabels(subjects, fontsize=10)
        
        # 添加数值
        for i in range(len(subjects)):
            for j in range(len(subjects)):
                text = ax.text(j, i, f'{matrix[i, j]:.2f}',
                              ha='center', va='center', 
                              color='white' if abs(matrix[i, j]) > 0.5 else 'black',
                              fontsize=9, fontweight='bold')
        
        ax.set_title('学科成绩相关性矩阵', fontsize=12, pad=10)
        cbar = self.correlation_canvas.figure.colorbar(im, ax=ax, label='相关系数')
        cbar.ax.tick_params(labelsize=9)
        self.correlation_canvas.figure.tight_layout(pad=1.5)
        self.correlation_canvas.draw()
        
        # 显示发现
        self.correlation_findings.setFont(QFont("Microsoft YaHei", 10))
        findings = []
        for subj1, subj2, corr in correlation['strong_correlations']:
            if corr > 0:
                findings.append(f"🔗 {subj1}与{subj2}正相关(系数{corr})：一科提升可能带动另一科")
            else:
                findings.append(f"⚡ {subj1}与{subj2}负相关(系数{corr})：需要平衡时间分配")
        
        if findings:
            self.correlation_findings.setText("\n".join(findings))
        else:
            self.correlation_findings.setText("未发现显著的学科关联性(相关系数>0.7)")
