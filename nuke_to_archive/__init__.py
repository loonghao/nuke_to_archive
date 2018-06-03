# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""
# Import nuke modules.
import nuke

# Import local modules.
from nuke_to_archive.core import NukeToArchive


def archive():
    start_archive = nuke.ask("Do you want to archive the nuke script?")
    if start_archive:
        nuke_to_archive = NukeToArchive()
        nuke_to_archive.start()
