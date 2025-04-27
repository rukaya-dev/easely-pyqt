from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QValidator, QRegularExpressionValidator
from datetime import datetime


class AlphaValidator(QValidator):
    def validate(self, string, pos):
        if all(char.isalpha() or char.isspace() for char in string):
            return QValidator.State.Acceptable, string, pos
        return QValidator.State.Invalid, string, pos


class DateValidator(QValidator):
    def validate(self, string, pos):
        date_format = "%a, %B %d, %Y"
        try:
            datetime.strptime(string, date_format)
            return QValidator.State.Acceptable, string, pos
        except ValueError:
            return QValidator.State.Invalid, string, pos


class AgeIntValidator(QValidator):
    def validate(self, string, pos):
        if all(char.isdigit() for char in string):
            if string:
                value = int(string)
                if 1 <= value <= 1440:
                    return QValidator.State.Acceptable, string, pos
            else:
                return QValidator.State.Intermediate, string, pos
        return QValidator.State.Invalid, string, pos


class PhoneNumberValidator(QValidator):
    def validate(self, string, pos):
        if not all(char.isdigit() for char in string):
            return QValidator.State.Invalid, string, pos

        if 11 <= len(string) <= 15:
            return QValidator.State.Acceptable, string, pos
        elif len(string) < 11:
            return QValidator.State.Intermediate, string, pos
        return QValidator.State.Invalid, string, pos


class AlphaNumUnderscoreValidator(QValidator):
    def __init__(self, parent=None):
        super(AlphaNumUnderscoreValidator, self).__init__(parent)
        self.regex = QRegularExpression("^(?=.*[a-zA-Z])[a-zA-Z0-9_]+$")

    def validate(self, string, pos):
        if self.regex.MatchOption.exactMatch(string):
            return QValidator.State.Acceptable, string, pos
        return QValidator.State.Invalid, string, pos

    def fixup(self, string):
        pass


normal_regex = QRegularExpression()
normal_input_validator = QRegularExpressionValidator(normal_regex)
normal_input_validator.setRegularExpression(normal_regex)

email_regex = QRegularExpression(r'^[a-z][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
email_validator = QRegularExpressionValidator(email_regex)
email_validator.setRegularExpression(email_regex)


national_id_number_regex = QRegularExpression(r"^[a-zA-Z0-9\- ]{5,20}$")
national_id_number_validator = QRegularExpressionValidator(national_id_number_regex)
national_id_number_validator.setRegularExpression(national_id_number_regex)


search_regex = QRegularExpression(r'^[A-Za-z0-9][A-Za-z0-9\s,.#\/&\-]*$')
search_input_validator = QRegularExpressionValidator(search_regex)
search_input_validator.setRegularExpression(search_regex)

phone_number_regex = QRegularExpression(r'^[0-9()+-]+$')
phone_number_validator = QRegularExpressionValidator(phone_number_regex)
phone_number_validator.setRegularExpression(phone_number_regex)


role_name_regex = QRegularExpression(r'^[a-zA-Z][a-zA-Z\s]*[a-zA-Z]$')
role_validator = QRegularExpressionValidator(role_name_regex)
role_validator.setRegularExpression(role_name_regex)

