#! /usr/bin/env python
import fixheader

PROJECT_NAME = 'IdioTest'
AUTHOR = 'Dietrich Epp <depp@zdome.net>'
LICENSE = [
    'This source code is licensed under the GNU General Public License,',
    'Version 3. See gpl-3.0.txt for details.'
]
EXCLUDE = set(['build', 'setup.py', 'header.py', 'test.py'])

class MyHeaderFixer(fixheader.HeaderFixer):
    def filter_path(self, path, isdir):
        if path in EXCLUDE:
            return False
        return super(MyHeaderFixer, self).filter_path(path, isdir)
    def project_name(self, path):
        return PROJECT_NAME
    def project_author(self, path):
        return AUTHOR
    def header_suffix(self, path):
        return LICENSE

MyHeaderFixer().run()
