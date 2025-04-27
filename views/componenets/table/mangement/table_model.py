from PyQt6 import QtCore
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt6.QtWidgets import QStyledItemDelegate, QHeaderView
from ast import literal_eval

from loggers.logger_configs import set_up_logger

logger = set_up_logger('main.views.components.table.management.table_model')


class TableModel(QAbstractTableModel):
    def __init__(self, table_name, column_display_names, data=None, data_columns=None):
        super().__init__()
        self._data = data
        self.column_mappings = data_columns
        self._columns = self.column_mappings.copy()
        self.start_after_id = None
        self.column_display_names = column_display_names
        self.table_name = table_name

    def rowCount(self, parent=None):
        if self._data:
            return len(self._data)
        else:
            return 0

    def columnCount(self, parent=None):
        return len(self._columns)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._data)):
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        column = index.column()
        data_row = self._data[index.row()]
        column_path = self.column_mappings[column].split('.')
        value = data_row

        for key in column_path:
            if not isinstance(value, dict) or key not in value:
                return None

            value = value[key]

            if isinstance(value, list):
                value = str(value)

        if self.table_name == "doctors_services_relation":
            value = self.process_doctors_services_relation_value(value)

        return value

    def process_doctors_services_relation_value(self, value):
        if isinstance(value, str):
            try:
                if value.startswith("[") or value.startswith('{'):
                    value = literal_eval(value)
                    if isinstance(value, list):
                        return ", ".join(str(item[next(iter(item.keys()))]) for item in value)
            except Exception as e:
                logger.error(e, exc_info=True)
        elif isinstance(value, dict):
            return f"{value.get('first_name', '')} {value.get('last_name', '')}"

        return value

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            # Use the adjusted column names for headers
            return self._columns[section]
        return None

    def removeRow(self, row, parent=QModelIndex()):
        """Remove a row from the model"""
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            del self._data[row]
            self.endRemoveRows()
            return True
        return False

    def setColumnOrder(self, new_order):
        """Set a new order of columns to display. Expects a list of column names."""
        self.beginResetModel()
        self._columns = [col for col in new_order if col in self.column_mappings]
        self.endResetModel()

    def hideColumns(self):
        """Hide specified columns. Expects a list of column names to hide."""
        self.beginResetModel()
        self._columns = [col for col in self.column_mappings if col not in self.columnsToHide]
        self.endResetModel()

    def headerData(self, section, orientation, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
            if section < len(self.column_display_names):
                # This assumes the columns in your SELECT statement are in the same order as in the database
                db_column_name = list(self.column_display_names.keys())[section]
                return self.column_display_names.get(db_column_name)
        return super().headerData(section, orientation, role)

    def updateData(self, new_data):
        self.beginResetModel()
        self._data = new_data
        # Reset columns to original on data update, or adapt as needed
        self._columns = self.column_mappings.copy()
        self.endResetModel()


class ElidedItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.textElideMode = Qt.TextElideMode.ElideLeft
        option.wrapText = False  # Ensuring that the text doesn't wrap


class HeaderView(QHeaderView):
    def __init__(self, orientation, parent=None):
        super(HeaderView, self).__init__(orientation, parent)

    def paintSection(self, painter, rect, logical_index):
        super(HeaderView, self).paintSection(painter, rect, logical_index)
