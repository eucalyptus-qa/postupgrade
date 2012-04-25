#!/usr/bin/python

import os
import re
import sys
import time

from euca_qa import helper
from euca_qa import euca_except_hook

class PostUpgrade(helper.AbstractHelper):
    def run_and_log(self, host, cmd):
        print "RUNNING on %s: %s" % (host.ip, cmd) 
        [ ret, out, err ] = host.run_command(cmd, return_output=True)
        if ret != 0:
            raise Exception("command '%s' returned code %d" % (cmd, ret))

    def run(self):
        ret = 0
        for host in self.config['hosts']:
            if host.has_role('clc'):
                try: 
                    # Get new credentials; otherwise EUARE commands will fail
                    self.run_and_log(host, 'while [ -z $S3_URL ]; do sleep 60; rm admin_cred.zip; euca_conf --get-credentials admin_cred.zip; unzip -o admin_cred.zip; source eucarc; done')
                    self.run_and_log(host, "source eucarc; python2.6 ./synthetic_data.py check")
                    self.run_and_log(host, "source eucarc; python2.6 ./synthetic_data.py clean")
                except Exception, e:
                    print "[TEST REPORT] FAILED " + str(e)
                    return 1
                return 0

if __name__ == "__main__":
    sys.excepthook = euca_except_hook(False, True)
    p = PostUpgrade()
    result = p.run()
    if result != 0:
        sys.exit(result)
    postrun = helper.DisableDNS()
    if not postrun.config['hosts'][0].getVersion().startswith('3'):
        result = postrun.run()
        if result != 0:
            print "[TEST REPORT] FAILED : DisableDNS returned %d" % result
        else:
            print "[TEST REPORT] SUCCESS"
        sys.exit(result)
