import os
import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QSlider, QFileDialog, QLabel, QLineEdit)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class ControlWindow(QWidget):
    def __init__(self, projector_window):
        super().__init__()
        self.projector = projector_window
        
        self.setWindowTitle("Painel de Controle - KGS Karaoke")
        self.resize(600, 450)
        
        self.setup_ui()
        self.setup_player()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Campo de Busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar vídeo por nome...")
        self.search_input.textChanged.connect(self.filter_playlist)
        layout.addWidget(self.search_input)
        
        # Lista de Reprodução (Fila)
        self.playlist_widget = QListWidget()
        # Garante a ordenação alfabética automática solicitada
        self.playlist_widget.setSortingEnabled(True)
        
        layout.addWidget(QLabel("Fila de Vídeos (Ordem Alfabética Automática):"))
        layout.addWidget(self.playlist_widget)
        
        # Botões de Ação da Fila
        fila_btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Adicionar Vídeos")
        self.btn_add.clicked.connect(self.add_music)
        fila_btn_layout.addWidget(self.btn_add)
        
        self.btn_remove = QPushButton("Remover Selecionado")
        self.btn_remove.clicked.connect(self.remove_music)
        fila_btn_layout.addWidget(self.btn_remove)
        
        layout.addLayout(fila_btn_layout)
        
        # Botões de Controle do Player
        player_btn_layout = QHBoxLayout()
        
        self.btn_play = QPushButton("Play / Pause")
        self.btn_play.clicked.connect(self.play_pause)
        player_btn_layout.addWidget(self.btn_play)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_music)
        player_btn_layout.addWidget(self.btn_stop)
        
        layout.addLayout(player_btn_layout)
        
        # Slider de Volume
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)
        vol_layout.addWidget(self.volume_slider)
        
        layout.addLayout(vol_layout)
        
        # Status
        self.status_label = QLabel("Pronto.")
        layout.addWidget(self.status_label)
        
    def setup_player(self):
        """Inicializa o QMediaPlayer e direciona o vídeo para a Janela do Projetor."""
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        
        # Conecta diretamente o reprodutor nativo ao QVideoWidget do projetor
        self.player.setVideoOutput(self.projector.video_widget)
        
        self.player.mediaStatusChanged.connect(self.media_status_changed)
        
    def add_music(self):
        """Abre o explorador para o usuário adicionar vídeos."""
        # getOpenFileNames para suportar seleção de múltiplos arquivos de uma vez
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Selecionar Vídeos", "", "Video Files (*.mp4 *.mkv *.avi)")
        
        for file_path in file_paths:
            if file_path:
                item_text = os.path.basename(file_path)
                
                # Verifica se a música já foi adicionada para evitar duplicatas
                existing_items = self.playlist_widget.findItems(item_text, Qt.MatchFlag.MatchExactly)
                if existing_items:
                    continue # Pula para o próximo arquivo se este já existir
                
                # Devido ao setSortingEnabled(True), isso já insere na posição alfabética correta
                self.playlist_widget.addItem(item_text)
                
                # Identifica o item inserido para anexar o caminho do arquivo
                items = self.playlist_widget.findItems(item_text, Qt.MatchFlag.MatchExactly)
                for item in items:
                    if item.data(Qt.ItemDataRole.UserRole) is None:
                        item.setData(Qt.ItemDataRole.UserRole, {
                            'video': file_path
                        })
                        break
            
    def filter_playlist(self, text):
        """Filtra a lista de vídeos de acordo com a busca do usuário."""
        search_term = text.lower()
        for i in range(self.playlist_widget.count()):
            item = self.playlist_widget.item(i)
            # Exibe o item se a busca for vazia ou se o termo estiver no nome
            item.setHidden(search_term not in item.text().lower())

    def remove_music(self):
        """Remove o vídeo selecionado da fila."""
        current_row = self.playlist_widget.currentRow()
        if current_row >= 0:
            self.playlist_widget.takeItem(current_row)

    def stop_music(self):
        """Interrompe o vídeo atual e volta para a tela de espera."""
        self.player.stop()
        self.btn_play.setText("Play / Pause")
        self.projector.show_idle_screen()
        self.status_label.setText("Parado.")
            
    def play_pause(self):
        """Inicia a reprodução do vídeo selecionado, ou alterna Pause/Play."""
        current_item = self.playlist_widget.currentItem()
        if not current_item:
            return

        data = current_item.data(Qt.ItemDataRole.UserRole)
        if not data:
            return

        selected_path = data.get('video')
        current_source = self.player.source().toLocalFile()

        # Se escolheu uma música diferente da que está carregada
        if selected_path != current_source:
            self.load_selected_item()
            self.player.play()
            self.btn_play.setText("Pause")
            self.projector.show_video()
            return

        # Alterna entre Play e Pause se for a mesma música
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("Play / Pause")
        else:
            self.player.play()
            self.btn_play.setText("Pause")
            self.projector.show_video()
            
    def load_selected_item(self):
        """Lê os dados do vídeo selecionado e prepara o Player."""
        current_item = self.playlist_widget.currentItem()
        if not current_item:
            if self.playlist_widget.count() > 0:
                self.playlist_widget.setCurrentRow(0)
                current_item = self.playlist_widget.currentItem()
            else:
                return
                
        data = current_item.data(Qt.ItemDataRole.UserRole)
        if data:
            video_path = data.get('video')
            self.player.setSource(QUrl.fromLocalFile(video_path))
            self.status_label.setText(f"Carregado: {os.path.basename(video_path)}")
                
    def change_volume(self, value):
        self.audio_output.setVolume(value / 100.0)
            
    def media_status_changed(self, status):
        """Se o vídeo terminar, mostra a pontuação e depois volta para a tela de idle do projetor."""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.btn_play.setText("Play / Pause")
            
            # Como não temos captação de microfone para evitar latência,
            # a pontuação é randômica para fins de entretenimento, como em muitas máquinas clássicas.
            score = random.randint(70, 100)
            self.projector.show_score(score)
            
            # Mostra o placar por 5 segundos e depois volta à tela de espera
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(5000, self.projector.show_idle_screen)
