"""
图表生成工具
使用Matplotlib生成各类分析图表
"""
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from typing import List, Dict, Optional
from io import BytesIO

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False


class ChartGenerator:
    """图表生成器"""
    
    @staticmethod
    def create_trend_chart(
        dates: List[str],
        scores: List[float],
        title: str = "成绩趋势",
        ylabel: str = "分数"
    ) -> Figure:
        """
        创建成绩趋势折线图
        
        Args:
            dates: 日期列表
            scores: 分数列表
            title: 图表标题
            ylabel: Y轴标签
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 5))
        
        x = range(len(scores))
        ax.plot(x, scores, 'b-o', linewidth=2, markersize=8)
        
        # 添加趋势线
        if len(scores) >= 2:
            z = np.polyfit(x, scores, 1)
            p = np.poly1d(z)
            ax.plot(x, p(x), 'r--', alpha=0.7, label='趋势线')
        
        ax.set_xlabel('考试')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_radar_chart(
        subjects: List[str],
        scores: List[float],
        title: str = "各科成绩对比"
    ) -> Figure:
        """
        创建雷达图（各科成绩对比）
        
        Args:
            subjects: 学科名称列表
            scores: 得分率列表（0-100）
            title: 图表标题
            
        Returns:
            matplotlib Figure对象
        """
        if not subjects or not scores:
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=16)
            ax.axis('off')
            return fig
        
        # 计算角度
        n = len(subjects)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
        
        # 闭合图形
        scores_plot = scores + [scores[0]]
        angles_plot = angles + [angles[0]]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        # 设置起始角度为顶部，顺时针方向
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # 绘制雷达图
        ax.fill(angles_plot, scores_plot, color='#667eea', alpha=0.25)
        ax.plot(angles_plot, scores_plot, color='#667eea', linewidth=2, marker='o', markersize=6)
        
        # 设置标签
        ax.set_xticks(angles)
        ax.set_xticklabels(subjects, fontsize=12, fontweight='bold')
        
        # 设置范围和刻度
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9, color='#718096')
        
        # 增强网格样式
        ax.grid(True, linestyle='--', alpha=0.5, color='#a0aec0')
        ax.spines['polar'].set_color('#e2e8f0')
        
        ax.set_title(title, fontsize=14, pad=20, fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_bar_chart(
        categories: List[str],
        values: List[float],
        title: str = "成绩统计",
        ylabel: str = "分数",
        color: str = 'steelblue'
    ) -> Figure:
        """
        创建柱状图
        
        Args:
            categories: 类别列表
            values: 数值列表
            title: 图表标题
            ylabel: Y轴标签
            color: 柱子颜色
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(categories))
        bars = ax.bar(x, values, color=color, alpha=0.8)
        
        # 在柱子上方显示数值
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.annotate(f'{val:.1f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
        
        ax.set_xlabel('学科')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_comparison_chart(
        categories: List[str],
        student_scores: List[float],
        class_avg: List[float],
        grade_avg: List[float],
        title: str = "成绩对比"
    ) -> Figure:
        """
        创建成绩对比柱状图（学生vs班级vs年级）
        
        Args:
            categories: 学科列表
            student_scores: 学生分数
            class_avg: 班级平均分
            grade_avg: 年级平均分
            title: 图表标题
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(categories))
        width = 0.25
        
        bars1 = ax.bar(x - width, student_scores, width, label='个人', color='steelblue')
        bars2 = ax.bar(x, class_avg, width, label='班级平均', color='orange')
        bars3 = ax.bar(x + width, grade_avg, width, label='年级平均', color='green')
        
        ax.set_xlabel('学科')
        ax.set_ylabel('分数')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_pie_chart(
        labels: List[str],
        sizes: List[float],
        title: str = "分布图"
    ) -> Figure:
        """
        创建饼图
        
        Args:
            labels: 标签列表
            sizes: 数值列表
            title: 图表标题
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, pctdistance=0.85)
        
        # 添加中心空白形成环形图
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_patch(centre_circle)
        
        ax.set_title(title)
        ax.axis('equal')
        
        return fig
    
    @staticmethod
    def create_multi_trend_chart(
        dates: List[str],
        subject_data: Dict[str, List[float]],
        title: str = "多学科成绩趋势"
    ) -> Figure:
        """
        创建多学科趋势对比图
        
        Args:
            dates: 日期列表
            subject_data: {学科名: 分数列表}
            title: 图表标题
            
        Returns:
            matplotlib Figure对象
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(dates))
        colors = plt.cm.tab10(np.linspace(0, 1, len(subject_data)))
        
        for (subject, scores), color in zip(subject_data.items(), colors):
            if len(scores) == len(dates):
                ax.plot(x, scores, '-o', label=subject, color=color, linewidth=2)
        
        ax.set_xlabel('考试')
        ax.set_ylabel('分数')
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def figure_to_bytes(fig: Figure) -> bytes:
        """将Figure转换为PNG字节数据"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return buf.getvalue()
    
    @staticmethod
    def close_figure(fig: Figure):
        """关闭Figure释放内存"""
        plt.close(fig)
