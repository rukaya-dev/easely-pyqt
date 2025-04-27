import os
import random
import re


def extract_file_extension(file_name):
    _, file_extension = os.path.splitext(file_name)
    return file_extension


def validate_file_size(file_name):
    file_size = os.path.getsize(file_name)
    return file_size <= 10 * 1024 * 1024


def convert_to_html_text(data):
    if data:
        html_content = ""

        # Loop through the dictionary to build the HTML content
        for key, value in data.items():
            html_content += f"<b>{key}:</b> <span>{value}</span><br/><br/>"
        html_content += "</body></html>"
        return html_content


def trim_text(text):
    info = (text[:9] + ' ...') if len(text) > 9 else text
    return info


def string_to_slug(s):
    s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'\s+', '_', s)

    return s


def random_color_generator():
    colors = ["#fecdd3", "#fbcfe8", "#f5d0fe", "#f5d0fe",
              "#e9d5ff", "#e9d5ff", "#ddd6fe", "#7dd3fc",
              "#c7d2fe", "#bfdbfe", "#a5f3fc", "#99f6e4", "#a7f3d0", "#d9f99d", "#fef08a", "#fde68a", "#fed7aa",
              "#fecaca", "#e5b3bb", "#e1b2c9", "#d3b0e3", "#d3b0e3",
              "#c2a5e6", "#c2a5e6", "#b5b1e6", "#69b9e3",
              "#a3a4e3", "#9bb2e3", "#91d4e3", "#84d4c4",
              "#8ed1b8", "#b7d480", "#d9e073", "#d3c96a",
              "#d3ae8a", "#e5acac", "#cc9c9c", "#b291b2"]
    return random.choice(colors)


def extract_names(full_name):
    name_parts = full_name.split()

    first_name = name_parts[0] if name_parts else ''

    last_name = name_parts[-1] if len(name_parts) > 1 else ''

    if len(name_parts) > 2:
        last_name = ' '.join(name_parts[1:])

    return first_name, last_name

