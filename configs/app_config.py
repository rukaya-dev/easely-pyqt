from PyQt6.QtCore import QLocale

from PyQt6.QtGui import QFontDatabase

FONT_ID = None
FONT_FAMILY = None

locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)


def load_fonts():
    global FONT_FAMILIES
    font_paths = [
        ":resources/fonts/Cambria/Cambria-Font-For-MAC.ttf",
        ":resources/fonts/Cambria/Cambria-Font-For-Windows.ttf",
        ":resources/fonts/Georgia/GeorgiaJoyDemoRegular.ttf",
        ":resources/fonts/Lato/Lato-Black.ttf",
        ":resources/fonts/Lato/Lato-BlackItalic.ttf",
        ":resources/fonts/Lato/Lato-Bold.ttf",
        ":resources/fonts/Lato/Lato-BoldItalic.ttf",
        ":resources/fonts/Lato/Lato-Italic.ttf",
        ":resources/fonts/Lato/Lato-Light.ttf",
        ":resources/fonts/Lato/Lato-LightItalic.ttf",
        ":resources/fonts/Lato/Lato-Regular.ttf",
        ":resources/fonts/Lato/Lato-Thin.ttf",
        ":resources/fonts/Lato/Lato-ThinItalic.ttf",
        ":resources/fonts/Poppins/Poppins-Black.ttf",
        ":resources/fonts/Poppins/Poppins-BlackItalic.ttf",
        ":resources/fonts/Poppins/Poppins-Bold.ttf",
        ":resources/fonts/Poppins/Poppins-BoldItalic.ttf",
        ":resources/fonts/Poppins/Poppins-ExtraBold.ttf",
        ":resources/fonts/Poppins/Poppins-ExtraBoldItalic.ttf",
        ":resources/fonts/Poppins/Poppins-ExtraLight.ttf",
        ":resources/fonts/Poppins/Poppins-ExtraLightItalic.ttf",
        ":resources/fonts/Poppins/Poppins-Italic.ttf",
        ":resources/fonts/Poppins/Poppins-LightItalic.ttf",
        ":resources/fonts/Poppins/Poppins-Medium.ttf",
        ":resources/fonts/Poppins/Poppins-MediumItalic.ttf",
        ":resources/fonts/Poppins/Poppins-Regular.ttf",
        ":resources/fonts/Poppins/Poppins-SemiBold.ttf",
        ":resources/fonts/Poppins/Poppins-SemiBoldItalic.ttf",
        ":resources/fonts/Poppins/Poppins-Thin.ttf",
        ":resources/fonts/Poppins/Poppins-ThinItalic.ttf",
        ":resources/fonts/Tahoma/TAHOMAB0.TTF",
        ":resources/fonts/Tahoma/TAHOMABD.TTF",
        ":resources/fonts/Tahoma/TAHOMA_0.TTF",
        ":resources/fonts/Tahoma/Tahoma Regular font.ttf",
        ":resources/fonts/arial/ARIBL0.ttf",
        ":resources/fonts/arial/ArialTh.ttf",
        ":resources/fonts/arial/Arialn.ttf",
        ":resources/fonts/arial/GEO_AI__.ttf",
        ":resources/fonts/arial/G_ari_bd.ttf",
        ":resources/fonts/arial/G_ari_i.ttf",
        ":resources/fonts/arial/arial.ttf",
        ":resources/fonts/calibri/Calibri Bold Italic.ttf",
        ":resources/fonts/calibri/Calibri Bold.ttf",
        ":resources/fonts/calibri/Calibri Italic.ttf",
        ":resources/fonts/calibri/Calibri Light Italic.ttf",
        ":resources/fonts/calibri/Calibri Light.ttf",
        ":resources/fonts/calibri/Calibri Regular.ttf",
        ":resources/fonts/garamond/GaramondLibre-Bold.otf",
        ":resources/fonts/garamond/GaramondLibre-Italic.otf",
        ":resources/fonts/garamond/GaramondLibre-Regular.otf",
        ":resources/fonts/helvetica/Helvetica-Bold.ttf",
        ":resources/fonts/helvetica/Helvetica-BoldOblique.ttf",
        ":resources/fonts/helvetica/Helvetica-Oblique.ttf",
        ":resources/fonts/helvetica/Helvetica.ttf",
        ":resources/fonts/helvetica/helvetica-compressed-5871d14b6903a.otf",
        ":resources/fonts/helvetica/helvetica-light-587ebe5a59211.ttf",
        ":resources/fonts/helvetica/helvetica-rounded-bold-5871d05ead8de.otf",
        ":resources/fonts/times_newer_roman/TimesNewerRoman-Bold.otf",
        ":resources/fonts/times_newer_roman/TimesNewerRoman-BoldItalic.otf",
        ":resources/fonts/times_newer_roman/TimesNewerRoman-Italic.otf",
        ":resources/fonts/times_newer_roman/TimesNewerRoman-Regular.otf",
        ":resources/fonts/trebuchet/Trebuchet-MS-Italic.ttf",
        ":resources/fonts/trebuchet/trebuc.ttf",
        ":resources/fonts/verdana/verdana-bold-italic.ttf",
        ":resources/fonts/verdana/verdana-bold.ttf",
        ":resources/fonts/verdana/verdana.ttf"
    ]
    font_families = []
    for path in font_paths:
        font_id = QFontDatabase.addApplicationFont(path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            font_families.extend(families)

    FONT_FAMILIES = font_families
    return font_families

def remove_dups(data):
    i = 0
    while i < len(data):
        j = i + 1
        while j < len(data):
            if data[i] == data[j]:
                del data[j]
            else:
                j += 1
        i += 1


def get_font_family():
    remove_dups(FONT_FAMILIES)
    return FONT_FAMILIES
