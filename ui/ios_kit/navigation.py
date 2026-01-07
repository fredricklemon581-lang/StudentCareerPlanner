# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QWidget, QStackedWidget, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPoint

class iOSNavigationController(QWidget):
    """
    iOS风格导航控制器
    支持 Push/Pop 转场动画
    """
    def __init__(self, root_view=None, parent=None):
        super().__init__(parent)
        self.stack = QStackedWidget(self)
        
        # 布局充满
        self.stack.setGeometry(self.rect())
        
        if root_view:
            self.push(root_view, animated=False)

    def resizeEvent(self, event):
        self.stack.setGeometry(self.rect())
        super().resizeEvent(event)
        
    def push(self, widget: QWidget, animated: bool = True):
        """推入新视图"""
        if self.stack.count() == 0:
            self.stack.addWidget(widget)
            self.stack.setCurrentWidget(widget)
            return

        current = self.stack.currentWidget()
        self.stack.addWidget(widget)
        
        if not animated:
            self.stack.setCurrentWidget(widget)
            return
            
        # 准备动画
        width = self.width()
        widget.setGeometry(width, 0, width, self.height()) # 初始位置在右侧外
        widget.show()
        widget.raise_()
        
        # 动画组
        self.anim_group = QParallelAnimationGroup()
        
        # 1. 新视图滑入 (从右向左)
        anim_in = QPropertyAnimation(widget, b"pos")
        anim_in.setDuration(400)
        anim_in.setStartValue(QPoint(width, 0))
        anim_in.setEndValue(QPoint(0, 0))
        anim_in.setEasingCurve(QEasingCurve.Type.OutQuart) # iOS风格曲线
        self.anim_group.addAnimation(anim_in)
        
        # 2. 旧视图视差滑动 (向左微移)
        anim_out = QPropertyAnimation(current, b"pos")
        anim_out.setDuration(400)
        anim_out.setStartValue(QPoint(0, 0))
        anim_out.setEndValue(QPoint(-width // 3, 0)) # 视差效果
        anim_out.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.anim_group.addAnimation(anim_out)
        
        def on_finished():
            self.stack.setCurrentWidget(widget)
            current.move(0, 0) # 重置位置以防万一
            # current.hide() # QStackedWidget会自动处理，但视差动画期间需要显示
            
        self.anim_group.finished.connect(on_finished)
        self.anim_group.start()
        
    def pop(self, animated: bool = True):
        """弹出当前视图"""
        if self.stack.count() <= 1:
            return
            
        current = self.stack.currentWidget()
        previous = self.stack.widget(self.stack.currentIndex() - 1)
        
        if not animated:
            self.stack.removeWidget(current)
            current.deleteLater()
            self.stack.setCurrentWidget(previous)
            return
            
        # 准备上一页
        width = self.width()
        previous.setGeometry(-width // 3, 0, width, self.height())
        previous.show()
        previous.raise_()
        current.raise_() # 当前页在最上层滑出
        
        self.anim_group = QParallelAnimationGroup()
        
        # 1. 当前视图滑出 (向右)
        anim_out = QPropertyAnimation(current, b"pos")
        anim_out.setDuration(400)
        anim_out.setStartValue(QPoint(0, 0))
        anim_out.setEndValue(QPoint(width, 0))
        anim_out.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.anim_group.addAnimation(anim_out)
        
        # 2. 上一页视差恢复
        anim_in = QPropertyAnimation(previous, b"pos")
        anim_in.setDuration(400)
        anim_in.setStartValue(QPoint(-width // 3, 0))
        anim_in.setEndValue(QPoint(0, 0))
        anim_in.setEasingCurve(QEasingCurve.Type.OutQuart)
        self.anim_group.addAnimation(anim_in)
        
        def on_finished():
            self.stack.removeWidget(current)
            current.deleteLater()
            self.stack.setCurrentWidget(previous)
            
        self.anim_group.finished.connect(on_finished)
        self.anim_group.start()
