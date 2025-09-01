from app.dao.connection import init_db
from app.ui.ui_main import MainWindow


def main():
    init_db()
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
