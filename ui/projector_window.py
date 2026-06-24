import os
import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter

class ConfettiWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.particles = []
        self.colors = [
            QColor("#FF3B30"), QColor("#FF9500"), QColor("#FFCC00"), 
            QColor("#4CD964"), QColor("#5AC8FA"), QColor("#007AFF"), 
            QColor("#5856D6"), QColor("#FF2D55")
        ]

        for _ in range(120):
            self.particles.append(self.create_particle(initial=True))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)

    def start(self):
        self.timer.start(30)

    def stop(self):
        self.timer.stop()

    def create_particle(self, initial=False):
        w = max(self.width(), 1920)
        h = max(self.height(), 1080)

        x = random.randint(0, w)
        y = random.randint(0, h) if initial else random.randint(-200, -20)
        size = random.randint(6, 14)
        speed_y = random.uniform(2.0, 5.0)
        speed_x = random.uniform(-1.5, 1.5)
        color = random.choice(self.colors)
        return [x, y, size, speed_y, speed_x, color]

    def update_particles(self):
        w = self.width()
        h = self.height()
        for p in self.particles:
            p[0] += p[4]
            p[1] += p[3]

            if p[1] > h:
                new_p = self.create_particle(initial=False)
                p[0], p[1], p[2], p[3], p[4], p[5] = new_p

            if p[0] < 0 or p[0] > w:
                p[4] *= -1

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for p in self.particles:
            painter.setBrush(p[5])
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(int(p[0]), int(p[1]), p[2], p[2])

class ProjectorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karaoke Projetor")
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtMultimediaWidgets import QVideoWidget
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)

        self.idle_container = QWidget(self)

        self.confetti = ConfettiWidget(self.idle_container)

        idle_layout = QVBoxLayout(self.idle_container)
        idle_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        idle_layout.setSpacing(30)

        self.logo_label = QLabel()
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Img', 'karaoke KGS.png')
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        idle_layout.addWidget(self.logo_label)

        self.idle_text = QLabel("Karaokê Pronto\nAguardando vídeo...")
        font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        self.idle_text.setFont(font)
        self.idle_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.idle_text.setStyleSheet("color: white;")

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(2, 2)
        self.idle_text.setGraphicsEffect(shadow)

        idle_layout.addWidget(self.idle_text)

        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setParent(self)
        self.score_label.hide()

        self.show_idle_screen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.idle_container.resize(self.size())
        self.confetti.resize(self.size())
        self.score_label.resize(self.size())

    def show_idle_screen(self):
        self.video_widget.hide()
        self.score_label.hide()
        self.idle_container.show()
        self.confetti.start()

    def show_video(self):
        self.confetti.stop()
        self.idle_container.hide()
        self.score_label.hide()
        self.video_widget.show()

    def show_score(self, score: int):
        self.video_widget.hide()
        self.confetti.stop()
        self.idle_container.hide()

        if score >= 90:
            color = "#FFD700" 
            msg = "Sensacional!"
        elif score >= 80:
            color = "#00FF00" 
            msg = "Muito Bom!"
        else:
            color = "#FFA500" 
            msg = "Bom!"

        self.score_label.setStyleSheet(f"color: {color}; background-color: transparent;")
        self.score_label.setText(f"{msg}\n\nSua Nota:\n{score}")
        self.score_label.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        self.score_label.show()
