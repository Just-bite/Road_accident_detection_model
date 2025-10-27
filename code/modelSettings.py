from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QHBoxLayout, QListWidget,
    QComboBox, QScrollArea, QCheckBox, QFrame,
    QListWidgetItem
)
from PyQt5.QtCore import Qt, QUrl

class ModelSettingsScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.build_ui()

    def build_ui(self):
        # ===== Левая панель =====
        left_panel = QVBoxLayout()
        export_btn = QPushButton("Export Model")
        left_panel.addWidget(export_btn)

        # Список моделей
        self.model_list = QListWidget()
        self.model_list.itemClicked.connect(self.on_model_selected)
        self.load_models()
        self.model_list.setMinimumHeight(200)  # минимальная высота для появления скролла

        # Оборачиваем список в QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        frame = QFrame()
        frame.setLayout(QVBoxLayout())
        frame.layout().addWidget(self.model_list)
        scroll_area.setWidget(frame)

        # Добавляем scroll_area с растяжкой
        left_panel.addWidget(scroll_area, stretch=1)
        self.layout.addLayout(left_panel, 2)

        # ===== Правая панель =====
        right_panel = QVBoxLayout()

        # Гибкие ряды для текста + комбобокс
        config_row = QHBoxLayout()
        config_label = QLabel("Hyperparameter configuration:")
        self.config_combo = QComboBox()
        config_row.addWidget(config_label)
        config_row.addWidget(self.config_combo)
        right_panel.addLayout(config_row)

        version_row = QHBoxLayout()
        version_label = QLabel("Model version:")
        self.version_combo = QComboBox()
        version_row.addWidget(version_label)
        version_row.addWidget(self.version_combo)
        right_panel.addLayout(version_row)

        # Чекбоксы
        self.check_seg = QCheckBox("Add segmentation visualisation")
        self.check_borders = QCheckBox("Add borders to objects")
        self.check_default = QCheckBox("Set this model as default")
        for cb in [self.check_seg, self.check_borders, self.check_default]:
            right_panel.addWidget(cb)

        # Кнопка Back справа
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.back_to_menu)
        right_panel.addWidget(back_btn, alignment=Qt.AlignRight)

        self.layout.addLayout(right_panel, 3)

    # --- Загрузка моделей ---
    def load_models(self):
        cur = self.parent.conn.cursor()
        cur.execute("SELECT id, name FROM models ORDER BY id")
        models = cur.fetchall()
        cur.close()

        self.model_list.clear()
        for mid, name in models:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, mid)
            self.model_list.addItem(item)

    # --- При выборе модели ---
    def on_model_selected(self, item):
        model_id = item.data(Qt.UserRole)
        cur = self.parent.conn.cursor()
        cur.execute("SELECT configurations, versions FROM models WHERE id = %s", (model_id,))
        result = cur.fetchone()
        cur.close()

        if result:
            configs, versions = result
            self.config_combo.clear()
            self.version_combo.clear()

            if configs:
                for cfg in configs:
                    self.config_combo.addItem(cfg)

            if versions:
                for ver in versions:
                    self.version_combo.addItem(ver)

    # --- Назад ---
    def back_to_menu(self):
        cur = self.parent.conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = %s", (self.parent.current_username,))
        role = cur.fetchone()[0]
        cur.close()
        self.parent.show_main_menu(self.parent.current_username, role)