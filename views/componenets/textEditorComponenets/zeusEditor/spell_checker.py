import enchant
from PyQt6.QtGui import QTextCharFormat, QColor


class SpellChecker:
    def __init__(self, text_widget, language='en_US'):
        self.text_widget = text_widget
        self.dictionary = enchant.DictWithPWL(language, "/Users/rukaya/MyProjects/PythonProject2/views/componenets/textEditorComponenets/zeusEditor/dictionary/medical.txt")
        self.text_widget.textChanged.connect(self.highlight_misspelled_words)

    def highlight_misspelled_words(self):
        # Disconnect the textChanged signal to avoid recursive calls
        self.text_widget.textChanged.disconnect(self.highlight_misspelled_words)

        text = self.text_widget.toPlainText()
        cursor = self.text_widget.textCursor()

        # Reset formatting to clear previous highlights
        cursor.select(cursor.Document)  # Select the entire document
        format = QTextCharFormat()
        format.setFontUnderline(False)  # Assuming white background
        cursor.mergeCharFormat(format)
        cursor.clearSelection()

        words = text.split()
        for word in words:
            if not word in self.text_widget.options_list:
                if not self.dictionary.check(word):
                    self.highlight_word(word)
        self.text_widget.textChanged.connect(self.highlight_misspelled_words)

    def highlight_word(self, word):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(True)  # Highlight for misspelled words
        fmt.setUnderlineColor(QColor("red"))  # Red underline for misspelled words
        cursor = self.text_widget.textCursor()
        text = self.text_widget.toPlainText()

        index = -1
        while True:
            index = text.find(word, index + 1)
            if index == -1:
                break

            # Check for word boundaries
            start_boundary = (index == 0 or not text[index - 1].isalnum())
            end_boundary = (index + len(word) == len(text) or not text[index + len(word)].isalnum())

            if start_boundary and end_boundary:
                cursor.setPosition(index)
                cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(word))
                cursor.mergeCharFormat(fmt)
