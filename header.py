#! /usr/bin/env python
import fixheader

class MyHeaderFixer(fixheader.HeaderFixer):
    PROJECT_NAME = 'IdioTest'
    AUTHOR = 'Dietrich Epp <depp@zdome.net>'
    HEADER_SUFFIX = [
        'This source code is licensed under the GNU General Public License,',
        'Version 3. See gpl-3.0.txt for details.'
        ]
    EXCLUDE = set(['build', 'setup.py', 'header.py', 'test.py'])

MyHeaderFixer().run()
