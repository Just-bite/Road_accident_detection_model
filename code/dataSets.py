import os
import shutil
from PyQt5.QtWidgets import (
    QListWidget, QListWidgetItem, QSlider, QMenuBar,
    QAction, QDialog, QPlainTextEdit, QFileDialog,  QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class DatasetsScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.root_path = r"E:\WTS\wts_dataset_zip\videos\val"
        self.current_path = self.root_path  # текущая директория

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # === Верхнее меню ===
        menu_bar = QMenuBar()

        # --- Edit (только для admin/analyst) ---
        cur = self.parent.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
        self.user_role = cur.fetchone()[0]
        cur.close()

        if self.user_role in ("admin", "analyst"):
            edit_menu = menu_bar.addMenu("Edit")

            add_action = QAction("Add (Ctrl+A)", self)
            add_action.setShortcut("Ctrl+A")
            add_action.triggered.connect(self.add_dataset)
            edit_menu.addAction(add_action)

            delete_action = QAction("Delete (Ctrl+D)", self)
            delete_action.setShortcut("Ctrl+D")
            delete_action.triggered.connect(self.delete_dataset)
            edit_menu.addAction(delete_action)

        # --- Help ---
        help_menu = menu_bar.addMenu("Help")
        help_action = QAction("How this works", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        self.layout.setMenuBar(menu_bar)

        # === Основная область ===
        main_area = QHBoxLayout()

        # --- Левая панель: список папок и видео ---
        left_panel = QVBoxLayout()
        self.path_label = QLabel(self.current_path)
        self.path_label.setStyleSheet("font-weight: bold; color: gray;")
        left_panel.addWidget(self.path_label)

        self.folder_list = QListWidget()
        self.folder_list.itemClicked.connect(self.on_item_clicked)
        left_panel.addWidget(self.folder_list)
        main_area.addLayout(left_panel, 2)

        # --- Правая панель: видео ---
        right_panel = QVBoxLayout()
        self.video_widget = QVideoWidget()
        self.video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_player.setVideoOutput(self.video_widget)
        right_panel.addWidget(self.video_widget, 5)

        # Панель управления видео
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

        self.play_btn.clicked.connect(self.video_player.play)
        self.pause_btn.clicked.connect(self.video_player.pause)
        self.stop_btn.clicked.connect(self.video_player.stop)
        self.slider.sliderMoved.connect(self.set_position)
        self.video_player.positionChanged.connect(self.position_changed)
        self.video_player.durationChanged.connect(self.duration_changed)

        right_panel.addLayout(controls)
        main_area.addLayout(right_panel, 4)

        self.layout.addLayout(main_area)

        # === Нижние кнопки ===
        bottom_bar = QHBoxLayout()
        self.up_btn = QPushButton("⬆️ Up")
        self.up_btn.clicked.connect(self.go_up)
        bottom_bar.addWidget(self.up_btn, alignment=Qt.AlignLeft)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_to_menu)
        bottom_bar.addWidget(back_btn, alignment=Qt.AlignLeft)

        self.layout.addLayout(bottom_bar)

        # Загрузка начальной папки
        self.load_folder(self.root_path)

    # === Загрузка содержимого папки ===
    def load_folder(self, path):
        self.folder_list.clear()
        self.current_path = path
        self.path_label.setText(path)

        try:
            items = os.listdir(path)
        except PermissionError:
            QMessageBox.warning(self, "Access Denied", f"Cannot access {path}")
            return

        folders = [f for f in items if os.path.isdir(os.path.join(path, f))]
        videos = [f for f in items if f.lower().endswith((".mp4", ".avi", ".mov"))]

        for folder in folders:
            item = QListWidgetItem(f"📁 {folder}")
            item.setData(Qt.UserRole, os.path.join(path, folder))
            item.setData(Qt.UserRole + 1, "folder")
            self.folder_list.addItem(item)

        for video in videos:
            item = QListWidgetItem(f"🎬 {video}")
            item.setData(Qt.UserRole, os.path.join(path, video))
            item.setData(Qt.UserRole + 1, "video")
            self.folder_list.addItem(item)

    # === Клик по элементу ===
    def on_item_clicked(self, item):
        path = item.data(Qt.UserRole)
        item_type = item.data(Qt.UserRole + 1)
        if item_type == "folder":
            self.load_folder(path)
        elif item_type == "video":
            self.play_video(path)

    # === Воспроизведение видео ===
    def play_video(self, path):
        url = QMediaContent(QUrl.fromLocalFile(path))
        self.video_player.setMedia(url)
        self.video_player.play()

    # === Навигация вверх ===
    def go_up(self):
        if self.current_path != self.root_path:
            parent_path = os.path.dirname(self.current_path)
            self.load_folder(parent_path)

    # === Работа со слайдером ===
    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.video_player.setPosition(position)

    # === Добавление видео ===
    def add_dataset(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select video files to add", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if not files:
            return
        for f in files:
            try:
                shutil.copy(f, self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to copy {f}:\n{e}")
        self.load_folder(self.current_path)

    # === Удаление видео ===
    def delete_dataset(self):
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No selection", "Select a video to delete.")
            return
        for item in selected_items:
            path = item.data(Qt.UserRole)
            item_type = item.data(Qt.UserRole + 1)
            if item_type != "video":
                continue
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete:\n{os.path.basename(path)}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    os.remove(path)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to delete {path}:\n{e}")
        self.load_folder(self.current_path)

    # === Окно помощи ===
    def show_help(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Help - Datasets")
        dlg.resize(700, 500)

        layout = QVBoxLayout()
        txt = QPlainTextEdit()
        txt.setReadOnly(True)
        txt.setStyleSheet("background-color: #000; color: #00FF00; font-family: Consolas; font-size: 13px;")
        txt.setPlainText("""
🟩 HOW DATASETS SCREEN WORKS

• Left side — folder and video list.
• Click a folder to open it.
• Click a video to play it on the right.
• Admins/Analysts can add/delete datasets via Edit menu (Ctrl+A / Ctrl+D).
• Use ⬆️ Up to return to the previous folder.
• Click Back to return to main menu.

🟩 COLOR SCHEME
Black background with green text for comfort and readability.
""")
        layout.addWidget(txt)
        dlg.setLayout(layout)
        dlg.exec_()

    # === Назад в главное меню ===
    def back_to_menu(self):
        cur = self.parent.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
        role = cur.fetchone()[0]
        cur.close()
        self.parent.show_main_menu(self.parent.current_username, role)
