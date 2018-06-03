# Import built-in modules.
import os.path as os_path

# Import Nuke modules.
import nuke

# Add current package to nuke plugin path.
nuke.pluginAddPath(
    os_path.join(os_path.dirname(__file__), 'nuke_to_archive', 'icons'))

toolbar = nuke.menu("Nodes")
hz_main_node = toolbar.addCommand(
    'Nuke To archive',
    "import nuke_to_archive;nuke_to_archive.archive()",
    icon="nuke_to_archive.png")
