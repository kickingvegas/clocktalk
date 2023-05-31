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
from enum import Enum

CLOCKTALK_VERSION="0.1.0"

DOMAIN = "com.apple.speech.synthesis.general.prefs"

def trapUnexpectedCondition(condition, message, exitStatus=1):
    sys.stderr.write("{condition}: {message}\n".format(condition=condition,
                                                     message=message))
    sys.exit(exitStatus)


class AnnouncePeriod(Enum):
    HOUR = "EveryHourInterval"
    HALF = "EveryHalfHourInterval"
    QUARTER = "EveryQuarterHourInterval"


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
            prog='clocktalk',
            description="""Command line utility to configure and enable periodic
            macOS time announcements.""",
            epilog="""This is a wrapper script around the command line tool
            `defaults` to configure the domain `{0}`.
            """.format(DOMAIN))

        
        add_argument = self.parser.add_argument
                
        add_argument('-v', '--version',
                     action='version',
                     version=CLOCKTALK_VERSION,
                     help='print version information and exit')

        add_argument('-p', '--period',
                     action='store',
                     default='hour',
                     choices=['hour', 'half', 'quarter'],
                     help="""period to annouce time (default hour)""")

        add_argument('-r', '--read',
                     action='store_true',
                     help="""read current configuration (all other arguments
                     ignored)""")

        add_argument('-e', '--enable',
                     action='store_true',
                     help="""enable periodic time announcements (default
                     is disabled if not present)
                     """)

        add_argument('-V', '--volume',
                     action='store',
                     type=volume_float_type,
                     default=0.5,
                     help="""set volume from 0.0 to 1.0 (default 0.5 if not present)""")

                
        add_argument('-x', '--execute',
                     action='store_true',
                     help='when present, execute the acutal `defaults` command')
        
    def run(self):
        return self.parser.parse_args()
        
class ClockTalk:
    def __init__(self, parsedArguments):
        self.version = CLOCKTALK_VERSION
        self.stdout = sys.stdout
        self.stdin = sys.stdin
        self.stderr = sys.stderr
        self.domain = DOMAIN
        self.parsedArguments = parsedArguments
        self.template = """{{ TimeAnnouncementPrefs = {{ TimeAnnouncementsEnabled = {enabled}; TimeAnnouncementsIntervalIdentifier = {interval}; TimeAnnouncementsPhraseIdentifier = ShortTime; TimeAnnouncementsVoiceSettings = {{ CustomVolume = \"{volume}\"; }};}};}}"""
                
    def run(self):
        cmdList = ['/usr/bin/defaults']

        if self.parsedArguments.read or len(sys.argv) < 2:
            cmdList.append('read')
            cmdList.append(self.domain)
            status = subprocess.call(cmdList, stdout=self.stdout)
            # wrap up 
            if self.stdout != sys.stdout:
                self.stdout.close()
            
            sys.exit(status)

        ## write operations

        plist = self.template.format(enabled=self.enabled(),
                                     interval=self.period().value,
                                     volume=self.parsedArguments.volume)

        cmdList.append('write')
        cmdList.append(self.domain)
        cmdList.append("{0}".format(plist))

        if self.parsedArguments.execute:
            status = subprocess.call(cmdList, stdout=self.stdout)
            # wrap up 
            if self.stdout != sys.stdout:
                self.stdout.close()
            
        else:
            sys.stdout.write(' '.join(cmdList) + '\n')


    def period(self):
        period = None
        if self.parsedArguments.period == 'hour':
            period = AnnouncePeriod.HOUR
        elif self.parsedArguments.period == 'half':
            period = AnnouncePeriod.HALF
        elif self.parsedArguments.period == 'quarter':
            period = AnnouncePeriod.QUARTER
        else:
            trapUnexpectedCondition("Error", "period is not defined.")

        return period


    def enabled(self):
        result = 1 if self.parsedArguments.enable else 0
        return result
        
if __name__ == '__main__':
    app = ClockTalk(CommandLineParser().run())
    app.run()
