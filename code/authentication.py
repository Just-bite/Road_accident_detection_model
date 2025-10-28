from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QInputDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AuthScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent


        self.layout_main = QVBoxLayout()
        self.layout_main.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout_main)


        self.setStyleSheet("background-color: #000000; color: white;")
        self.show_home()

    def clear_layout(self):
        while self.layout_main.count():
            child = self.layout_main.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_input(self, placeholder, enter_next=None, return_func=None):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedWidth(250)
        inp.setFont(QFont("Courier New", 11))
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #111111;
                color: white;
                border: 2px solid #00FF00;
                border-radius: 10px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border-color: #00FFAA;
            }
        """)
        if enter_next:
            inp.returnPressed.connect(lambda: enter_next.setFocus())
        if return_func:
            inp.returnPressed.connect(return_func)
        return inp

    def show_home(self):
        self.clear_layout()


        self.layout_main.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

        title = QLabel("Welcome to Road Detection Model")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Courier New", 32, QFont.Bold))
        title.setStyleSheet("background-color: transparent;")
        self.layout_main.addWidget(title, alignment=Qt.AlignCenter)

        self.layout_main.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Minimum))

        sign_up_btn = QPushButton("Sign Up")
        sign_in_btn = QPushButton("Sign In")
        for btn, color in [(sign_up_btn, "#00FF00"), (sign_in_btn, "#00FF00")]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedWidth(200)
            btn.setFont(QFont("Courier New", 12, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: white;
                    background-color: #111111;
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 6px 15px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: black;
                }}
            """)

        sign_up_btn.clicked.connect(self.show_sign_up)
        sign_in_btn.clicked.connect(self.show_sign_in)

        self.layout_main.addWidget(sign_up_btn, alignment=Qt.AlignCenter)
        self.layout_main.addWidget(sign_in_btn, alignment=Qt.AlignCenter)


        self.layout_main.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def show_sign_up(self):
        self.clear_layout()
        self.layout_main.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

        title = QLabel("Sign Up")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Courier New", 24, QFont.Bold))
        title.setStyleSheet("background-color: transparent;")
        self.layout_main.addWidget(title, alignment=Qt.AlignCenter)

        self.layout_main.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.username_input = self.create_input("Enter username")
        self.activator_input = self.create_input("Enter activator code (optional)")
        self.username_input.returnPressed.connect(self.activator_input.setFocus)
        self.activator_input.returnPressed.connect(self.register_user)

        register_btn = QPushButton("Register")
        back_btn = QPushButton("Back")
        for btn, color in [(register_btn, "#00FF00"), (back_btn, "#FF0000")]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedWidth(200)
            btn.setFont(QFont("Courier New", 12, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: white;
                    background-color: #111111;
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 6px 15px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: black;
                }}
            """)
        register_btn.clicked.connect(self.register_user)
        back_btn.clicked.connect(self.show_home)

        for w in [self.username_input, self.activator_input, register_btn, back_btn]:
            self.layout_main.addWidget(w, alignment=Qt.AlignCenter)

        self.layout_main.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

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

        if username.lower() == "admin":
            if activator_code != "admin":
                QMessageBox.warning(self, "Error", "Invalid activator for admin.")
                cur.close()
                return
            role = "admin"
            activator_id = None
        elif not activator_code:
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
            "INSERT INTO users (username, password, role, activator_id) VALUES (%s,%s,%s,%s)",
            (username, 'default_pass', role, activator_id)
        )
        self.parent.conn.commit()
        cur.close()
        QMessageBox.information(self, "Success", f"User '{username}' registered as '{role}'.")
        self.show_home()

    def show_sign_in(self):
        self.clear_layout()
        self.layout_main.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))

        title = QLabel("Sign In")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Courier New", 24, QFont.Bold))
        title.setStyleSheet("background-color: transparent;")
        self.layout_main.addWidget(title, alignment=Qt.AlignCenter)

        self.layout_main.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum,QSizePolicy.Minimum))

        self.signin_username_input = self.create_input("Enter username", return_func=self.sign_in_user)

        login_btn = QPushButton("Login")
        back_btn = QPushButton("Back")
        for btn, color in [(login_btn, "#00FF00"), (back_btn, "#FF0000")]:
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedWidth(200)
            btn.setFont(QFont("Courier New", 12, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: white;
                    background-color: #111111;
                    border: 2px solid {color};
                    border-radius: 12px;
                    padding: 6px 15px;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: black;
                }}
            """)
        login_btn.clicked.connect(self.sign_in_user)
        back_btn.clicked.connect(self.show_home)

        for w in [self.signin_username_input, login_btn, back_btn]:
            self.layout_main.addWidget(w, alignment=Qt.AlignCenter)

        self.layout_main.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

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
            if role == "admin":
                activator, ok = QInputDialog.getText(self, "Admin Activator", "Enter admin activator code:")
                if not ok or activator != "admin":
                    QMessageBox.warning(self, "Error", "Invalid admin activator.")
                    return
            self.parent.current_username = username
            self.parent.user_role = role
            self.parent.show_main_menu(username, role)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))