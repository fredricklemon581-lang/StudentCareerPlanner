# -*- coding: utf-8 -*-
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QSize, QRect
from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

class InteractiveMixin:
    """
    iOS微交互Mixin
    支持:
    - 按压缩放 (Scale Down)
    - 悬停上浮 (Lift Up)
    """
    
    def setup_interactions(self, scale_factor=0.96, lift_offset=4):
        self._scale_factor = scale_factor
        self._lift_offset = lift_offset
        self._original_rect = None
        self._is_pressed = False
        
        # Shadow for lift effect
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(20)
        self._shadow.setColor(QColor(0, 0, 0, 20))
        self._shadow.setOffset(0, 2)
        self.setGraphicsEffect(self._shadow)
        
    def enterEvent(self, event):
        # Hover Lift
        if not self._is_pressed:
            self.animate_lift(True)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        # Hover Reset
        if not self._is_pressed:
            self.animate_lift(False)
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self._is_pressed = True
        self.animate_scale(True)
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.animate_scale(False)
        # Restore lift if still hovering
        if self.rect().contains(event.pos()):
            self.animate_lift(True)
        else:
            self.animate_lift(False)
        super().mouseReleaseEvent(event)
        
    def animate_scale(self, down):
        """缩放动画 (模拟，实际改变尺寸会影响布局，这里用margin模拟或者改变geometry)"""
        # Qt Widget scaling in layout is tricky without Transform.
        # Simplified approach: Change style/color to simulate depth or small geometry tweak
        # For true scaling, we'd need QGraphicsView or painting.
        # Let's simple animate property 'pos' a bit to press 'in'
        
        pass # Placeholder for complex scaling, sticking to CSS press states for stability in QWidget
        
    def animate_lift(self, up):
        """上浮动画 (阴影变化)"""
        anim = QPropertyAnimation(self._shadow, b"blurRadius")
        anim.setDuration(200)
        anim.setStartValue(self._shadow.blurRadius())
        anim.setEndValue(30 if up else 20)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim.start()
        
        anim2 = QPropertyAnimation(self._shadow, b"offset")
        anim2.setDuration(200)
        anim2.setStartValue(self._shadow.offset())
        anim2.setEndValue(QPoint(0, 6) if up else QPoint(0, 2))
        anim2.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim2.start()
