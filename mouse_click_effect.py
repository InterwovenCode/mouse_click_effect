# 参考资料：
#   - [水波纹特效的C++模拟](https://www.cnblogs.com/that-boy/p/12310365.html)
#   - [实现水波纹显示效果（by 豪）](https://codebus.cn/contributor/hao-water-ripple-effect)
#   - [利用C/C++实现的水波纹特效](https://blog.csdn.net/qq_63303370/article/details/132794536)

from plugin import *
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "site-packages"))
from pynput import mouse
from qfluentwidgets import (
    FluentIcon as FIF,
)

# 添加水波纹特效的动画实现
class ClickWaterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.painter = QPainter()
        self.initAnimation()

    def initAnimation(self):
        self.m_waterDropAnimation = QVariantAnimation(self)
        self.m_animationRadius = 10
        self.m_waterDropColor = QColor(Qt.GlobalColor.yellow)
        self.m_waterDropColor.setAlpha(15)
        # self.m_waterDropColor = QColor(0, 0, 0, 15)
        self.WATER_DROP_RADIUS = 40

    # def sltRaduisChanged(self, value:QVariant):
    #     self.m_animationRadius = int(value)
    #     self.update()

    def sltRaduisChanged(self, value:QVariant):
        self.m_animationRadius = int(value)
        self.update()

    def showEvent(self, a0):
        if self.m_waterDropAnimation:
            self.m_waterDropAnimation.setStartValue(0)
            self.m_waterDropAnimation.setEndValue(self.WATER_DROP_RADIUS)
            self.m_waterDropAnimation.setDuration(380)

            self.m_waterDropAnimation.valueChanged.connect(self.sltRaduisChanged)
            self.m_waterDropAnimation.finished.connect(self.close)
            self.m_waterDropAnimation.start()
        return super().showEvent(a0)

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.m_waterDropColor))

        waterDropPath = QPainterPath()
        waterDropPath.addEllipse(QPoint(self.WATER_DROP_RADIUS, self.WATER_DROP_RADIUS), self.WATER_DROP_RADIUS, self.WATER_DROP_RADIUS)

        hidePath = QPainterPath()
        waterDropPath.addEllipse(QPoint(self.WATER_DROP_RADIUS, self.WATER_DROP_RADIUS), self.m_animationRadius, self.m_animationRadius)

        waterDropPath = waterDropPath - hidePath
        painter.drawPath(waterDropPath)
        return super().paintEvent(a0)

class ClickEffectWindow(QWidget):
    globalClicked = pyqtSignal(object, object, object)
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlag(Qt.WindowType.WindowTransparentForInput, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.globalClicked.connect(self.onGlobalClicked)
        self.lastClickPos = QCursor.pos()

    def onGlobalClicked(self, pos, button, pressed):
        self.lastClickPos = pos
        if button == mouse.Button.left and pressed:
            self.clickWidget = ClickWaterWidget()
            self.clickWidget.resize(QSize(100, 100))
            self.clickWidget.move(pos - QPoint(50, 50))
            self.clickWidget.show()

    def onClick(self, x, y, button, pressed):
        currentPosition = QPoint(x / self.devicePixelRatioF(), y / self.devicePixelRatioF())
        self.globalClicked.emit(currentPosition, button, pressed)

    def showEvent(self, a0):
        self.mouseHook = mouse.Listener(on_click=self.onClick)
        self.mouseHook.start()
        return super().showEvent(a0)

    def closeEvent(self, a0):
        self.mouseHook.stop()
        return super().closeEvent(a0)

class MouseClickEffect(PluginInterface):
    def __init__(self):
        super().__init__()
        self.effectWnd = None

    @property
    def previewImages(self) -> list:
        return []

    @property
    def name(self):
        return "MouseClickEffect"

    @property
    def displayName(self):
        return "鼠标点击特效"

    @property
    def desc(self):
        return "添加桌面鼠标滑动特效，目前只有一个水纹效果"

    @property
    def author(self) -> str:
        return "yaoxuanzhi"

    @property
    def icon(self):
        return FIF.ALBUM

    @property
    def version(self) -> str:
        return "v0.0.1"

    @property
    def url(self) -> str:
        return "https://github.com/InterwovenCode/mouse_click_effect"

    @property
    def tags(self) -> list:
        return ["click","effect"]


    def onChangeEnabled(self):
        if self.enable:
            self.effectWnd = ClickEffectWindow()
            self.effectWnd.show()
        else:
            self.effectWnd.close()
            self.effectWnd = None