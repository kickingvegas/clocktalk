#!/usr/bin/env python3
#
# Copyright 2023 Charles Y. Choi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import getopt
import argparse
import subprocess
import shutil
import json
import plistlib
from enum import Enum

GENCLOCKTALKD_VERSION="0.1.0"

DOMAIN = "com.apple.speech.synthesis.general.prefs"

def trapUnexpectedCondition(condition, message, exitStatus=1):
    sys.stderr.write("{condition}: {message}\n".format(condition=condition,
                                                     message=message))
    sys.exit(exitStatus)


def volume_float_type(arg):
    """ Type function for argparse - a float within some predefined bounds """
    try:
        f = float(arg)
    except ValueError:    
        raise argparse.ArgumentTypeError("Must be a floating point number")
    
    if 0.0 < f <= 1.0:
        pass
    else:
        raise argparse.ArgumentTypeError("Argument must be within ({0}, {1}]".format(str(0.0), str(1.0)))
    return f    


class CommandLineParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog='genclocktalkd',
            description="""Command line utility to generate `launchd` script to
            schedule `clocktalk`.""",
            epilog="""This utility will create a `launchd` script to invoke the `clocktalk` utility.
            """)
        
        add_argument = self.parser.add_argument
                
        add_argument('-v', '--version',
                     action='version',
                     version=GENCLOCKTALKD_VERSION,
                     help='print version information and exit')

        add_argument('-t', '--time',
                     nargs='+',
                     help="""24-hour time stamp (HH:MM), multiple times are
                     space separated""")

        add_argument('-w', '--workdir',
                     action='store',
                     default=os.getcwd(),
                     help="""work directory to run `launchd` script (default is
                     your current directory)""")

        add_argument('-P', '--path-to-clocktalk',
                     action='store',
                     default='{0}/bin/clocktalk'.format(os.environ['HOME']),
                     help='full path to `clocktalk` (default is your $HOME/bin)')

        add_argument('-l', '--label',
                     action='store',
                     required=True,
                     help="""`launchd` label""")

        add_argument('-p', '--period',
                     action='store',
                     default='hour',
                     choices=['hour', 'half', 'quarter'],
                     help="""`clocktalk` argument: period to annouce time (default hour)""")

        add_argument('-e', '--enable',
                     action='store_true',
                     help="""`clocktalk` argument: enable periodic time announcements (default
                     is disabled if not present)
                     """)

        add_argument('-V', '--volume',
                     action='store',
                     type=volume_float_type,
                     default=0.5,
                     help="""`clocktalk` argument: set volume from 0.0 to 1.0 (default 0.5 if not present)""")
                
        add_argument('-x', '--execute',
                     action='store_true',
                     help='`clocktalk` argument: when present, execute the acutal `defaults` command')

        add_argument('-j', '--json',
                     action='store_true',
                     help='output json to stdout')
                
        
    def run(self):
        return self.parser.parse_args()
        
class GenClockTalkD:
    def __init__(self, parsedArguments):
        self.version = GENCLOCKTALKD_VERSION
        self.stdout = sys.stdout
        self.stdin = sys.stdin
        self.stderr = sys.stderr
        self.domain = DOMAIN
        self.parsedArguments = parsedArguments
                
    def run(self):
        def parseTimestamp(buf):
            bufList = buf.split(':')
            hour = int(bufList[0])
            minutes = int(bufList[1])
            return { 'Hour': hour, 'Minute': minutes }

        timestamps = list(map(parseTimestamp, self.parsedArguments.time))

        programArguments = [self.parsedArguments.path_to_clocktalk]

        if self.parsedArguments.execute:
            programArguments.append('--execute')

        if self.parsedArguments.enable:
            programArguments.append('--enable')

        if self.parsedArguments.period:
            programArguments.append('--period')
            programArguments.append(self.parsedArguments.period)

        if self.parsedArguments.volume:
            programArguments.append('--volume')
            programArguments.append('{}'.format(self.parsedArguments.volume))

        launchdDict = {
            'StartCalendarinterval': timestamps,
            'WorkingDirectory': self.parsedArguments.workdir,
            'ProgramArguments': programArguments,
            'Label': self.parsedArguments.label
        }

        if self.parsedArguments.json:
            jsonBuf = json.dumps(launchdDict, indent=4)
            self.stdout.write(jsonBuf + '\n')

        outfileName = '{}.plist'.format(self.parsedArguments.label)
        
        with open(outfileName, 'wb') as outfile:
            plistlib.dump(launchdDict, outfile)

        # wrap up 
        if self.stdout != sys.stdout:
            self.stdout.close()

if __name__ == '__main__':
    app = GenClockTalkD(CommandLineParser().run())
    app.run()
