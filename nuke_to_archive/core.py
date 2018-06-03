"""Nuke to archive."""
# Import built-in modules.
import ConfigParser
import os
import re
import shutil
import threading
import time
import zipfile
from os.path import join as joinpath

# Import Nuke modules.
import nuke


class NukeToArchive(threading.Thread):

    def __init__(self):
        super(NukeToArchive, self).__init__()
        script_dir = os.path.dirname(__file__)
        profile = joinpath(script_dir, 'profile.ini')
        nuke_file = nuke.Root().name()
        if not nuke_file:
            nuke.message('Please save your nuke script first.')
        self.source_dir = os.path.dirname(nuke_file)
        if os.path.exists(profile):
            cf = ConfigParser.ConfigParser()
            cf.read(profile)
            self.source_dir = cf.get("root", "path")
        self.task = None
        self.filter = ['Read', 'ReadGeo2', 'ReadGeo']
        self.base_name = os.path.basename(nuke_file).split('.')[0]
        self.pack_dir = joinpath(self.source_dir, self.base_name)
        self.nuke_version = nuke.NUKE_VERSION_STRING
        if not os.path.exists(self.pack_dir):
            os.makedirs(self.pack_dir)
        self.pack_ = '[file dirname [value root.name]]/'

    def to_zip(self):
        dir_name = self.pack_dir
        zip_file_name = joinpath(self.source_dir,
                                 '{0}.zip'.format(self.base_name))
        file_list = []
        if os.path.isfile(dir_name):
            file_list.append(dir_name)
        else:
            for root, dirs, files in os.walk(dir_name):
                for name in files:
                    file_list.append(os.path.join(root, name))

        zf = zipfile.ZipFile(zip_file_name, "w", zipfile.zlib.DEFLATED, True)
        prog_incr = 100.0 / len(file_list)
        for i, tar in enumerate(file_list):
            if self.task.isCancelled():
                nuke.executeInMainThread(nuke.message, args=('cancel',))
                return
            self.task.setProgress(int(i * prog_incr))
            arcname = tar[len(dir_name):]
            self.task.setMessage("compressed %s files.." % arcname)
            zf.write(tar, arcname)
        zf.close()
        time.sleep(2)

    @staticmethod
    def check_format(filepath):
        m = re.match(r'(.+)(%\d+d|#+)', filepath)
        return not bool(m)

    @staticmethod
    def unified_path_format(filepath):
        return filepath.replace('\\', '/')

    def run(self):
        self.task = nuke.ProgressTask("NukeToPacking....")
        pack_dir = self.pack_dir + '/'
        pack_dir = self.unified_path_format(pack_dir)
        reads = [
            n for n in nuke.allNodes(recurseGroups=True)
            if n.Class() in self.filter
        ]
        prog_incr = 100.0 / len(reads)
        for i, n in enumerate(reads):
            if self.task.isCancelled():
                nuke.executeInMainThread(nuke.message, args=('cancel',))
                return
            self.task.setProgress(int(i * prog_incr))
            file_ = n['file'].getValue()
            # if n.Class == 'Read':
            #     frame_first = n['first'].getValue()
            #     frame_last = n['last'].getValue()
            self.task.setMessage("Copy %s files.." % n.fullName())
            if self.check_format(file_):
                m = re.compile(r'(?P<root_dir>(\w:/))')
                match_ = m.match(file_)
                if match_:
                    old_file = file_
                    file_root = match_.groupdict()['root_dir']
                    file_ = file_.replace(file_root, pack_dir)
                    file_ = self.unified_path_format(file_)
                    new_dir = os.path.dirname(file_)
                    if not os.path.exists(new_dir):
                        os.makedirs(new_dir)
                    print old_file, new_dir, 'single'
                    if not os.path.isfile(new_dir):
                        shutil.copy2(old_file, new_dir)
                    n['file'].setValue(file_.replace(pack_dir, self.pack_))
            else:
                dir_ = os.path.dirname(file_)
                for f in os.listdir(dir_):
                    seq_file_ = dir_ + "/" + f
                    m = re.compile(r'(?P<root_dir>([a-zA-Z]:/)(.+?/))')
                    match_ = m.match(seq_file_)
                    if match_:
                        old_file = seq_file_
                        # file_name, _, ext = old_file.split('.')
                        file_root = match_.groupdict()['root_dir']
                        seq_file_ = seq_file_.replace(file_root, pack_dir)
                        seq_file_ = self.unified_path_format(seq_file_)
                        new_dir = os.path.dirname(seq_file_)
                        if not os.path.exists(new_dir):
                            os.makedirs(new_dir)
                        # TODO need fix copy from node frame range
                        # for frame in range(frame_first, frame_last):
                        #     temp_file = '{0}.{1}.{2}'.format(file_name, frame, ext)
                        #     print temp_file, new_dir
                        if not os.path.isfile(new_dir):
                            shutil.copy2(old_file, new_dir)
                m = re.compile(r'(?P<root_dir>(\w:/)(.+?/))')
                match_ = m.match(file_)
                if match_:
                    file_root = match_.groupdict()['root_dir']
                    n['file'].setValue(file_.replace(file_root, self.pack_))
        nuke.scriptSaveAs(
            joinpath(self.pack_dir, '{0}.nk'.format(self.base_name)),
            overwrite=True)
        with open(joinpath(self.pack_dir, 'nuke2pack.info'), 'w') as f:
            f.write('Nuke: {0}'.format(self.nuke_version))
        self.to_zip()
        time.sleep(2)

        # def run_to_pack(self):
        #     threading.Thread(None, self.convert).start()

