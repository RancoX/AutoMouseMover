import sys
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout

class Worker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = True

    def run(self):
        while self.is_running:
            # Simulate some long-running task
            for i in range(100):
                if not self.is_running:
                    break
                self.progress.emit(i)
            self.finished.emit()

    def stop(self):
        self.is_running = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        self.button = QPushButton('Start')
        self.end_button = QPushButton('End')

        self.button.clicked.connect(self.start)
        self.end_button.clicked.connect(self.stop)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.end_button)
        self.setLayout(layout)

    def start(self):
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)

        self.thread.start()

    def stop(self):
        self.worker.stop()
        self.thread.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())