import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    def on_login(user):
        login.close()
        window = MainWindow(user)
        window.show()

    login = LoginWindow()
    login.login_success.connect(on_login)
    login.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()