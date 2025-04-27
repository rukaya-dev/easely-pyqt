import asyncio
import os
import sys

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from qasync import QEventLoop

from configs.app_config import load_fonts
from loggers.logger_configs import set_up_logger
import resources

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_FONT_DPI"] = "96"
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "Round"



class AppRunner:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.create_required_folders_and_files()

        self.app.setWindowIcon(QIcon(":/resources/images/application_icon.png"))
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_Use96Dpi)

        self.loop = QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)

        load_fonts()
        set_up_logger('main')
        self.apply_styles()

        from views.layouts.main_window_layout import MainWindowView

        self.main_window = MainWindowView(self)
        self.main_window.showMaximized()

        self.run_event_loop()

    def apply_styles(self):
        self.app.setStyle("Fusion")
        self.app.setStyleSheet("""
                    QWidget {
                        background-color: white;
                    }
                    QMessageBox QLabel {
                        color: black;
                    }
                    QMessageBox {
                        color:black;
                    }
                    QLabel {
                        color:black;
                        background-color:transparent;
                    }
                    QToolTip {
                        border: 1px solid transparent;
                        border-radius: 5px;
                        color:black;
                        background-color:white;
                    }
                    QScrollArea {
                            border:0;
                        }
                        QScrollBar:vertical {
                            background: transparent;
                            width: 8px; 
                            margin: 0px;
                        }

                        QScrollBar::handle:vertical {
                            background-color: rgba(0, 0, 0, 50); /* Semi-transparent handle */
                            min-height: 20px; /* Minimum height for the handle */
                            border-radius: 4px; /* Rounded corners for the handle */
                        }
                        QScrollBar::handle:vertical:hover {
                            background-color: rgba(0, 0, 0, 50); /* Slightly darker on hover */
                        }

                        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                            height: 0px; /* No buttons at the ends */
                            border: none;
                            background: none;
                        }

                        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                            background: none;
                        }

                        QScrollBar:horizontal {
                            border: none;
                            background: transparent;
                            height: 8px; /* Thin horizontal scrollbar */
                            margin: 0px;
                        }

                        QScrollBar::handle:horizontal {
                            background-color: rgba(0, 0, 0, 140); /* Semi-transparent handle */
                            min-width: 20px; /* Minimum width for the handle */
                            border-radius: 4px; /* Rounded corners for the handle */
                        }

                        QScrollBar::handle:horizontal:hover {
                            background-color: rgba(0, 0, 0, 140); /* Slightly darker on hover */
                        }

                        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                            width: 0px; /* No buttons at the ends */
                            border: none;
                            background: none;
                        }

                        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                            background: none;
                        }
                """)

    def create_required_folders_and_files(self):
        app_folder = os.path.join(os.path.dirname(sys.argv[0]), "database/local")
        db_file_path = os.path.join(app_folder, "app.db")
        log_file_path = os.path.join(app_folder, "app.log")

        # Create the main app folder if it doesn't exist
        if not os.path.exists(app_folder):
            os.makedirs(app_folder)

        # Create the log file if it doesn't exist
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as log_file:
                log_file.write("")

    def run_event_loop(self):
        with self.loop:
            try:
                self.loop.run_forever()
            finally:
                # After the loop stops, we can close it safely
                self.loop.close()

    def stop_application(self):
        # Cancel all running tasks
        tasks = asyncio.all_tasks(self.loop)
        for task in tasks:
            task.cancel()
        # Schedule the loop to stop in a thread-safe way
        self.loop.call_soon_threadsafe(self.loop.stop)


def main():
    QtCore.QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    global app_runner
    app_runner = AppRunner()



if __name__ == "__main__":
    main()
