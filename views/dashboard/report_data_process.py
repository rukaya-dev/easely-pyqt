from PyQt6.QtCore import QThread, pyqtSignal
import pandas as pd


class ReportDataProcessor(QThread):
    data_is_ready = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        try:
            df = pd.DataFrame(self.data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['month'] = df['created_at'].dt.strftime('%B')
            self.data_is_ready.emit(df)
        except Exception as e:
            self.error.emit(str(e))
