import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QMessageBox, QHBoxLayout
from qasync import asyncSlot

from signals import SignalRepositorySingleton
from views.componenets.customsComponents.custom_combobox import CustomComboBox
from views.componenets.customsComponents.table.form_componenets.custom_label import CustomLabel
from views.componenets.customsComponents.table.save_and_cancel_buttons import SaveAndCancelButtonsWithLoader


class UpdateReportStatusDialog(QDialog):
    def __init__(self, controller, report_id, parent=None):
        super().__init__(parent)

        self.parent = parent
        self.report_id = report_id

        # Signals
        self.signals = SignalRepositorySingleton.instance()

        self.reports_controller = controller

        self.combo_style_sheet = """
        QComboBox {
            border:1px solid #C7C7C7;
            border-radius:7px;
            background-color:white;
            color:black;
            padding-left:10px;
            padding-right:5px;
        }
        QComboBox QAbstractItemView 
        {
            min-width: 150px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 0px;
            padding-right:5px;
        }
        QComboBox::down-arrow {
            image: url(:resources/icons/expand_more.svg);
        }

        QComboBox::down-arrow:on { /* shift the arrow when popup is open */
            top: 1px;
            left: 1px;
        }
        """

        report_status_label = CustomLabel(name="Report Status")

        self.report_status_combo = CustomComboBox()
        self.report_status_combo.setFixedWidth(400)
        self.report_status_combo.setStyleSheet(self.combo_style_sheet)

        self.report_status_model = QStandardItemModel()
        self.report_status_combo.setModel(self.report_status_model)

        self.save_and_cancel_btns = SaveAndCancelButtonsWithLoader(text="Update")
        self.save_and_cancel_btns.save_btn.clicked.connect(self.update_report_status)
        self.save_and_cancel_btns.cancel_btn.clicked.connect(self.close)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        controls_layout.addWidget(self.save_and_cancel_btns, 1, Qt.AlignmentFlag.AlignRight)

        report_status_layout = QVBoxLayout()
        report_status_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        report_status_layout.setContentsMargins(0, 0, 0, 0)
        report_status_layout.setSpacing(10)

        report_status_layout.addWidget(report_status_label)
        report_status_layout.addWidget(self.report_status_combo)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addLayout(report_status_layout)
        layout.addLayout(controls_layout, Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setFixedSize(500, 200)

    @asyncSlot()
    async def populate_statuses(self):
        report_statuses = [
            {'name': 'Drafted', 'description': 'The report is currently being created and is not yet finalized.'},
            {'name': 'Reviewed',
             'description': 'The report has been reviewed and approved by the necessary personnel.'},
            {'name': 'Revised',
             'description': 'The report has been modified after review and needs a final check.'},
            {'name': 'Finalized',
             'description': 'The report is complete and no further edits are allowed. It\'s ready to be shared or archived.'},
            {'name': 'Released',
             'description': 'The report has been shared with the patient or other healthcare providers.'},
            {'name': 'Archived',
             'description': 'The report is no longer actively needed and has been stored securely for historical reference.'}
        ]
        for item in report_statuses:
            standard_item = QStandardItem()
            standard_item.setData(item["name"], Qt.ItemDataRole.DisplayRole)
            standard_item.setToolTip(item["description"])
            self.report_status_model.appendRow(standard_item)

    @asyncSlot()
    async def update_report_status(self):
        self.save_and_cancel_btns.save_btn.start()
        status = self.report_status_combo.currentText()
        data = {"status": status, "updated_at": datetime.datetime.now().isoformat()}
        res = await self.reports_controller.update_report(
            self.parent.table_view.get_current_id(),
            data)
        if not res:
            self.save_and_cancel_btns.save_btn.stop()
            msg = QMessageBox()
            msg.setText('Error occurred')
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setDetailedText(
                "error occurred while updating report status, please contact your service provider.")
            msg.exec()
        else:
            self.save_and_cancel_btns.save_btn.stop()
            self.signals.globalReportUpdateTableViewSignal.emit()
            self.close()
            msg = QMessageBox()
            msg.setText('Report Status Successfully Updated.')
            msg.setIcon(QMessageBox.Icon.Information)
            msg.exec()