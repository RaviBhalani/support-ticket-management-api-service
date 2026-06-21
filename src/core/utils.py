import os

from src.core.constants import TEMPLATES_DIR


def read_template(caller_file: str, template_name: str) -> str:
    path = os.path.join(os.path.dirname(caller_file), TEMPLATES_DIR, template_name)
    with open(path) as f:
        return f.read()
