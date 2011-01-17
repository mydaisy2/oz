# Copyright (C) 2010  Chris Lalancette <clalance@redhat.com>

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import Guest
import shutil
import subprocess
import re
import ozutil
import RedHat

class RHEL3Guest(RedHat.RedHatCDGuest):
    def __init__(self, tdl, config):
        self.tdl = tdl
        self.ks_file = ozutil.generate_full_auto_path("rhel-3-jeos.ks")

        if self.tdl.installtype != 'url':
            raise Guest.OzException("RHEL-3 installs must be done via url")

        self.url = self.tdl.url

        ozutil.deny_localhost(self.url)

        RedHat.RedHatCDGuest.__init__(self, "RHEL-3", self.tdl.update,
                                      self.tdl.arch, 'url', None, None, None,
                                      None, config)

    def modify_iso(self):
        self.log.debug("Putting the kickstart in place")

        shutil.copy(self.ks_file, self.iso_contents + "/ks.cfg")

        self.log.debug("Modifying the boot options")
        f = open(self.iso_contents + "/isolinux/isolinux.cfg", "r")
        lines = f.readlines()
        f.close()
        for line in lines:
            if re.match("timeout", line):
                lines[lines.index(line)] = "timeout 1\n"
            elif re.match("default", line):
                lines[lines.index(line)] = "default customiso\n"
        lines.append("label customiso\n")
        lines.append("  kernel vmlinuz\n")
        lines.append("  append initrd=initrd.img ks=cdrom:/ks.cfg method=" + self.url + "\n")

        f = open(self.iso_contents + "/isolinux/isolinux.cfg", "w")
        f.writelines(lines)
        f.close()

    def generate_install_media(self, force_download):
        self.log.info("Generating install media")
        self.get_original_iso(self.url + "/images/boot.iso", force_download)
        self.copy_iso()
        self.modify_iso()
        self.generate_iso()
        self.cleanup_iso()

def get_class(tdl, config):
    if tdl.update in ["GOLD", "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9"]:
        return RHEL3Guest(tdl, config)
    raise Guest.OzException("Unsupported RHEL-3 update " + tdl.update)
