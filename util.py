import os

from constants import template_dir

def template_path(template):
    path = os.path.join(
        os.path.dirname(__file__) + template_dir, 
        template
    )
    return path
