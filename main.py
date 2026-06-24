import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from ui.control_window import ControlWindow
from ui.projector_window import ProjectorWindow

class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, image_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(500, Qt.TransformationMode.SmoothTransformation)

        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1200)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.finished.connect(self.on_fade_in_finished)

    def start(self):
        self.show()
        self.animation.start()

    def on_fade_in_finished(self):
        QTimer.singleShot(1500, self.start_fade_out)

    def start_fade_out(self):
        self.animation.finished.disconnect(self.on_fade_in_finished)
        self.animation.finished.connect(self.on_fade_out_finished)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def on_fade_out_finished(self):
        self.close()
        self.finished.emit()

def launch_app(app, projector, control):

    screens = app.screens()
    if len(screens) > 1:
        second_screen = screens[1]
        projector.setGeometry(second_screen.geometry())
        projector.showFullScreen()
    else:
        projector.resize(1024, 768)
        projector.show()

    control.show()

def main():
    if sys.platform == 'win32':
        import ctypes
        myappid = 'kgs.karaoke.video.player.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)

    image_path = os.path.join(os.path.dirname(__file__), 'Img', 'karaoke KGS.png')
    app.setWindowIcon(QIcon(image_path))

    styles_path = os.path.join(os.path.dirname(__file__), 'ui', 'styles.qss')
    if os.path.exists(styles_path):
        with open(styles_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())

    projector = ProjectorWindow()
    control = ControlWindow(projector)

    if os.path.exists(image_path):
        splash = SplashScreen(image_path)
        splash.finished.connect(lambda: launch_app(app, projector, control))
        splash.start()
    else:
        launch_app(app, projector, control)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
