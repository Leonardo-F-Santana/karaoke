import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.control_window import ControlWindow
from ui.projector_window import ProjectorWindow

def main():
    app = QApplication(sys.argv)
    
    # Carregar estilos globais (QSS) para o Dark Mode
    styles_path = os.path.join(os.path.dirname(__file__), 'ui', 'styles.qss')
    if os.path.exists(styles_path):
        with open(styles_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
            
    # Criar instâncias das janelas
    projector = ProjectorWindow()
    control = ControlWindow(projector)
    
    # Lógica de suporte a múltiplos monitores
    screens = app.screens()
    if len(screens) > 1:
        # Pega o segundo monitor
        second_screen = screens[1]
        
        # Move a geometria da janela para dentro dos limites do segundo monitor
        projector.setGeometry(second_screen.geometry())
        
        # Exibe em tela cheia no segundo monitor
        projector.showFullScreen()
    else:
        # Se só tiver um monitor, exibe como uma janela maximizada ou redimensionada 
        # para que o usuário não perca o acesso à Janela de Controle
        projector.resize(1024, 768)
        projector.show()
        
    # Exibe a Janela de Controle no monitor principal
    control.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
