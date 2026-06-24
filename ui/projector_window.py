from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtMultimediaWidgets import QVideoWidget

class ProjectorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Karaoke Projetor")
        self.setStyleSheet("background-color: #000000;")
        
        # Oculta a barra de título para tela cheia limpa
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Layout que preenche toda a tela com margens zeradas
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Adiciona o widget de vídeo nativo
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget)
        
        # Mensagem de idle (quando não há vídeo rodando)
        self.idle_label = QLabel("Karaokê Pronto\n\nAguardando vídeo...")
        font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        self.idle_label.setFont(font)
        self.idle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.idle_label.setStyleSheet("color: #4DA8DA; background-color: transparent;")
        self.idle_label.setParent(self)
        
        self.show_idle_screen()
        
    def resizeEvent(self, event):
        """Mantém a label de idle sempre centralizada."""
        super().resizeEvent(event)
        self.idle_label.resize(self.size())

    def show_idle_screen(self):
        """Oculta o player e mostra a mensagem de espera."""
        self.video_widget.hide()
        self.idle_label.show()
        
    def show_video(self):
        """Exibe o player e oculta a mensagem de espera."""
        self.idle_label.hide()
        self.video_widget.show()
