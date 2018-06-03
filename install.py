# Import built-in modules.
import os
import shutil

# Current path.
ROOT = os.path.dirname(__file__)

# C:\Users\{user_name}\.nuke
NUKE_PATH = os.path.join(os.environ['USERPROFILE'], '.nuke')

shutil.copy2(os.path.join(ROOT, 'nuke_path', 'menu.py'), NUKE_PATH)

shutil.rmtree(os.path.join(NUKE_PATH, 'nuke_to_archive'))
shutil.copytree(
    os.path.join(ROOT, 'nuke_to_archive'),
    os.path.join(NUKE_PATH, 'nuke_to_archive'))
