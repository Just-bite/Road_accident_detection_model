from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox,
)
from PyQt5.QtCore import Qt

class AuthScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.show_home()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_home(self):
        self.clear_layout()
        title = QLabel("Welcome to Road Detection Model")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 15px;")

        sign_up_btn = QPushButton("Sign Up")
        sign_in_btn = QPushButton("Sign In")
        sign_up_btn.setFixedWidth(200)
        sign_in_btn.setFixedWidth(200)

        sign_up_btn.clicked.connect(self.show_sign_up)
        sign_in_btn.clicked.connect(self.show_sign_in)

        self.layout.addWidget(title, alignment=Qt.AlignCenter)
        self.layout.addWidget(sign_up_btn, alignment=Qt.AlignCenter)
        self.layout.addWidget(sign_in_btn, alignment=Qt.AlignCenter)

    # --- Sign Up ---
    def show_sign_up(self):
        self.clear_layout()

        title = QLabel("Sign Up")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.activator_input = QLineEdit()
        self.activator_input.setPlaceholderText("Enter activator code (optional)")

        register_btn = QPushButton("Register")
        back_btn = QPushButton("Back")
        register_btn.setFixedWidth(200)
        back_btn.setFixedWidth(200)

        register_btn.clicked.connect(self.register_user)
        back_btn.clicked.connect(self.show_home)

        for w in [title, self.username_input, self.activator_input, register_btn, back_btn]:
            self.layout.addWidget(w, alignment=Qt.AlignCenter)

    def register_user(self):
        username = self.username_input.text().strip()
        activator_code = self.activator_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Input Error", "Username is required.")
            return

        cur = self.parent.conn.cursor()

        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            QMessageBox.warning(self, "Error", "Username already exists.")
            cur.close()
            return

        # Если активатор не указан → observer
        if not activator_code:
            role = "observer"
            activator_id = None
        else:
            cur.execute("SELECT id, role, is_used FROM activators WHERE activator_code = %s", (activator_code,))
            activator = cur.fetchone()
            if not activator:
                QMessageBox.warning(self, "Error", "Activator code does not exist.")
                cur.close()
                return

            activator_id, role, is_used = activator
            if is_used:
                QMessageBox.warning(self, "Error", "This activator has already been used.")
                cur.close()
                return
            cur.execute("UPDATE activators SET is_used = TRUE WHERE id = %s", (activator_id,))

        cur.execute(
            "INSERT INTO users (username, password, role, activator_id) VALUES (%s, %s, %s, %s)",
            (username, 'default_pass', role, activator_id)
        )
        self.parent.conn.commit()
        cur.close()

        QMessageBox.information(self, "Success", f"User '{username}' registered as '{role}'.")
        self.show_home()

    # --- Sign In ---
    def show_sign_in(self):
        self.clear_layout()

        title = QLabel("Sign In")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")

        self.signin_username_input = QLineEdit()
        self.signin_username_input.setPlaceholderText("Enter username")
        login_btn = QPushButton("Login")
        back_btn = QPushButton("Back")
        login_btn.setFixedWidth(200)
        back_btn.setFixedWidth(200)

        login_btn.clicked.connect(self.sign_in_user)
        back_btn.clicked.connect(self.show_home)

        for w in [title, self.signin_username_input, login_btn, back_btn]:
            self.layout.addWidget(w, alignment=Qt.AlignCenter)

    def sign_in_user(self):
        username = self.signin_username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Please enter a username.")
            return

        try:
            cur = self.parent.conn.cursor()
            cur.execute("SELECT role FROM users WHERE username = %s", (username,))
            result = cur.fetchone()
            cur.close()

            if not result:
                QMessageBox.warning(self, "Error", "User not found.")
                return

            role = result[0]

            # Сохраняем в родителе
            self.parent.current_username = username
            self.parent.user_role = role

            # Переходим в главное меню
            self.parent.show_main_menu(username, role)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
