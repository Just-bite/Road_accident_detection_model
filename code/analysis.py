from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QMessageBox,
    QComboBox, QSlider, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt, QUrl

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class StartAnalysisScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.selected_video_path = None  # путь для пользовательского видео

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.build_ui()

    def build_ui(self):
        # --- Заголовок ---
        header_layout = QHBoxLayout()
        header_label = QLabel("Video input:")
        self.video_combo = QComboBox()
        self.video_combo.addItems(["Test video 1", "Test video 2", "Test video 3", "From datasets"])
        self.video_combo.currentIndexChanged.connect(self.play_selected_video)

        add_btn = QPushButton("Add Video")
        add_btn.clicked.connect(self.add_video)

        header_layout.addWidget(header_label)
        header_layout.addWidget(self.video_combo)
        header_layout.addWidget(add_btn)
        self.layout.addLayout(header_layout)

        # --- Чекбоксы и Analyze ---
        options_layout = QHBoxLayout()
        self.generate_report_cb = QCheckBox("Generate report")
        self.add_diagrams_cb = QCheckBox("Add diagrams")
        analyze_btn = QPushButton("Analyze")
        analyze_btn.clicked.connect(self.analyze_video)

        options_layout.addWidget(self.generate_report_cb)
        options_layout.addWidget(self.add_diagrams_cb)
        options_layout.addWidget(analyze_btn)
        self.layout.addLayout(options_layout)

        # --- Видео-просмотр ---
        self.video_widget = QVideoWidget()
        self.layout.addWidget(self.video_widget, stretch=5)

        self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_player.setVideoOutput(self.video_widget)

        controls = QHBoxLayout()
        self.play_btn = QPushButton("▶️")
        self.pause_btn = QPushButton("⏸️")
        self.stop_btn = QPushButton("⏹️")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)

        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(self.slider)
        self.layout.addLayout(controls)

        # Связь кнопок и слайдера с плеером
        self.play_btn.clicked.connect(self.video_player.play)
        self.pause_btn.clicked.connect(self.video_player.pause)
        self.stop_btn.clicked.connect(self.video_player.stop)
        self.slider.sliderMoved.connect(self.set_position)
        self.video_player.positionChanged.connect(self.position_changed)
        self.video_player.durationChanged.connect(self.duration_changed)

        # --- Кнопка Back в правом нижнем углу ---
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.close_screen)
        self.layout.addWidget(back_btn, alignment=Qt.AlignRight | Qt.AlignBottom)

    # === Методы для управления видео ===
    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.video_player.setPosition(position)

    def play_selected_video(self):
        video_name = self.video_combo.currentText()
        test_videos = {
            "Test video 1": r"E:\WTS\wts_dataset_zip\test_videos\video1.mp4",
            "Test video 2": r"E:\WTS\wts_dataset_zip\test_videos\video2.mp4",
            "Test video 3": r"E:\WTS\wts_dataset_zip\test_videos\video3.mp4"
        }

        if video_name in test_videos:
            path = test_videos[video_name]
        elif video_name == "From datasets":
            path, _ = QFileDialog.getOpenFileName(
                self, "Select video from dataset", r"E:\WTS\wts_dataset_zip\videos\val",
                "Video Files (*.mp4 *.avi *.mov)"
            )
            self.selected_video_path = path
        else:
            path = self.selected_video_path

        if path:
            self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.video_player.play()

    def add_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select video file", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if path:
            self.selected_video_path = path
            # Добавляем новый элемент в комбобокс, если еще нет
            if self.video_combo.findText("User Video") == -1:
                self.video_combo.addItem("User Video")
            self.video_combo.setCurrentText("User Video")

    def analyze_video(self):
        video_name = self.video_combo.currentText()
        report_flag = self.generate_report_cb.isChecked()
        diagrams_flag = self.add_diagrams_cb.isChecked()

        # Проверка выбранного видео
        if video_name == "From datasets" and not self.selected_video_path:
            QMessageBox.warning(self, "No video", "Please select a video from dataset or add your own.")
            return

        # Здесь должна быть логика анализа
        QMessageBox.information(self, "Analysis", f"Analyzing video: {video_name}\n"
                                                  f"Generate report: {report_flag}\n"
                                                  f"Add diagrams: {diagrams_flag}")

    def close_screen(self):
        self.video_player.stop()
        # Получаем роль корректно через курсор
        cur = self.parent.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
        role = cur.fetchone()[0]
        cur.close()
        self.parent.show_main_menu(self.parent.current_username, role)