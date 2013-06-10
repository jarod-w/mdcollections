#!/usr/bin/python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Refer to the README and COPYING files for full details of the license
#
import os
import sys
import optparse
import shutil
import tempfile

class Usage(Exception):
    def __init__(self, msg = None, no_error = False):
        Exception.__init__(self, msg, no_error)

class ArgumentCheck(Exception):
    def __init__(self, msg = None, no_error = False):
        Exception.__init__(self, msg, no_error)

class HGMarkdownParser:
    """
    Add new specific syntax: [[CCODE/CPPCODE/PYTHONCODE]] filepath
    The class arms at parsing the new specific syntax into our md.
    """

    CODESIGNLIST = ("[[CCODE]]", "[[CPPCODE]]", "[[PYTHONCODE]]")

    def __init__(self, mdfile):
        self.markdownFile = mdfile
        self.tfd, self.tname = tempfile.mkstemp()

    def _readCodeFile(self, codefile):
        if not os.path.exists(codefile):
            print "The code file " + codefile + " doesn't exist"
        with open(codefile) as f:
            return f.read();

    def _replaceHGCode(self, sign, codefile):
        if "CCODE" in sign:
            os.write(self.tfd, "```c\n")
        elif "CPPCODE" in sign:
            os.write(self.tfd, "```c++\n")
        elif "PYTHONCODE" in sign:
            os.write(self.tfd, "```python\n")
        os.write(self.tfd, self._readCodeFile(codefile))
        os.write(self.tfd, "```")

    def _parseMarkdownFile(self):
        with open(self.markdownFile, "r+") as f:
            for line in f.readlines():
                if line.strip().startswith("[[CCODE]]"):
                    codefile = line[10:].strip()
                    self._replaceHGCode("[[CCODE]]", codefile)
                elif line.strip().startswith("[[CPPCODE]]"):
                    codefile = line[12:].strip()
                    self._replaceHGCode("[[CPPCODE]]", codefile)
                elif line.strip().startswith("[[PYTHONCODE]]"):
                    codefile = line[15:].strip()
                    self._replaceHGCode("[[PYTHONCODE]]", codefile)
                else:
                    os.write(self.tfd, line)
            print self.tname
            os.close(self.tfd)

    def _renameTmpName(self):
        shutil.move(self.tname, self.markdownFile+".new")

    def execute(self):
        #parse markdown file and write them into tmp file
        self._parseMarkdownFile()
        #rename the tmp name into originname+.new
        self._renameTmpName()
        return True

def parse_options():
    parser = optparse.OptionParser();

    parser.add_option("-f", "--file", dest="mdfile", type="string",
                     help="markdown file")

    (options, args) = parser.parse_args()

    if not options.mdfile:
        raise Usage("Error: Must input markdown file ")

    return options

def main():
    try:
        options = parse_options()
    except Usage, (msg, no_error):
        if no_error:
            out = sys.stdout
            ret = 0
        else:
            out = sys.stderr
            ret = 2
        if msg:
            print >> out, msg
        return ret

    hgmp = HGMarkdownParser(options.mdfile)
    if hgmp.execute():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
