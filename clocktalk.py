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
import argparse
import subprocess
import json
import plistlib
import shutil
from enum import Enum
from tempfile import NamedTemporaryFile

CLOCKTALK_VERSION="0.1.2"

DOMAIN = "com.apple.speech.synthesis.general.prefs"

def trapUnexpectedCondition(condition, message, exitStatus=1):
    sys.stderr.write("{condition}: {message}\n".format(condition=condition,
                                                     message=message))
    sys.exit(exitStatus)

class AnnouncePeriod(Enum):
    HOUR = "EveryHourInterval"
    HALF = "EveryHalfHourInterval"
    QUARTER = "EveryQuarterHourInterval"


def floatBoundsTest(f, min=0.0, max=1.0, minInclusive=True, maxInclusive=True):
    if (minInclusive == False) and (maxInclusive == False):
        return (min < f < max)
    elif (minInclusive == False) and (maxInclusive == True):
        return (min < f <= max)
    elif (minInclusive == True) and (maxInclusive == False):
        return (min <= f < max)
    elif (minInclusive == True) and (maxInclusive == True):
        return (min <= f <= max)
    else:
        trapUnexpectedCondition('Error',
                                'floatBoundsTest failure: {0}, ({1}, {2})'
                                .format(f, min, max))
    
def volume_float_type(arg):
    """ Type function for argparse - a float within some predefined bounds """
    min = 0.3
    max = 1.0
    return generic_float_type(arg, min, max)

def rate_float_type(arg):
    """ Type function for argparse - a float within some predefined bounds """
    min = 0.5
    max = 2.0
    return generic_float_type(arg, min, max)

def generic_float_type(arg, min, max):
    try:
        f = float(arg)
    except ValueError:    
        raise argparse.ArgumentTypeError("Must be a floating point number")
    
    if not floatBoundsTest(f, min=min, max=max):
        raise argparse.ArgumentTypeError("Argument must be within [{0}, {1}]".format(str(min), str(max)))
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

        add_argument('-d', '--debug',
                     action='store_true',
                     default=False,
                     help="""debug mode; temp.plist will be created if --execute
                     flag is present""")
                
        add_argument('-e', '--enable',
                     action='store_true',
                     default=False,
                     help="""enable periodic time announcements (default
                     is disabled if not present)
                     """)

        add_argument('-p', '--period',
                     action='store',
                     default='hour',
                     choices=['hour', 'half', 'quarter'],
                     help="""period to annouce time (default hour)""")

        add_argument('-r', '--read',
                     action='store_true',
                     help="""read current configuration (all other arguments
                     ignored)""")

        add_argument('-R', '--rate',
                     action='store',
                     type=rate_float_type,
                     help="""set speech rate from 0.5 to 2.0 (disabled if not present)""")
        
        add_argument('-v', '--version',
                     action='version',
                     version=CLOCKTALK_VERSION,
                     help='print version information and exit')
        
        add_argument('-V', '--volume',
                     action='store',
                     type=volume_float_type,
                     default=0.5,
                     help="""set volume from 0.3 to 1.0 (default 0.5 if not present)""")

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
        plistDict = self.domainDict(self.parsedArguments.enable,
                                    self.interval(self.parsedArguments.period),
                                    self.parsedArguments.volume,
                                    self.parsedArguments.rate)

        if self.parsedArguments.execute:
            outfileName = self.writePlistFile(plistDict)
            cmdList.append('import')
            cmdList.append(self.domain)
            cmdList.append(outfileName)
            
            status = subprocess.call(cmdList, stdout=self.stdout)
            if status != 0:
                trapUnexpectedCondition('Error',
                                        'call to defaults failed. {0}'.format(' '.join(cmdList)))

            if self.parsedArguments.debug:
                shutil.copyfile(outfileName, 'temp.plist')
                
            if outfileName and os.path.exists(outfileName):
                os.unlink(outfileName)
            
            # wrap up 
            if self.stdout != sys.stdout:
                self.stdout.close()

        else:
            sys.stdout.write(json.dumps(plistDict, indent=4) + '\n')

    def interval(self, argPeriod):
        result = None
        if argPeriod == 'hour':
            result = AnnouncePeriod.HOUR
        elif argPeriod == 'half':
            result = AnnouncePeriod.HALF
        elif argPeriod == 'quarter':
            result = AnnouncePeriod.QUARTER
        else:
            trapUnexpectedCondition("Error", "interval is not defined.")
            
        return result.value

    def domainDict(self,
                   timeAnnouncementEnabled,
                   interval,
                   volume,
                   rate):
        plistDict = {}
        plistDict['TimeAnnouncementPrefs'] = {
            'TimeAnnouncementsEnabled': timeAnnouncementEnabled,
            'TimeAnnouncementsIntervalIdentifier': interval,
            'TimeAnnouncementsPhraseIdentifier' : 'ShortTime',
            'TimeAnnouncementsVoiceSettings': {
                'CustomVolume': volume
            }
        }

        if rate is not None:
            voiceSettings = plistDict['TimeAnnouncementPrefs']['TimeAnnouncementsVoiceSettings']
            voiceSettings['CustomRelativeRate'] = rate
            
        return plistDict


    def writePlistFile(self, plistDict):
        outfileName = None

        with NamedTemporaryFile(mode='wb',
                                prefix='clocktalk_',
                                suffix='.plist',
                                delete=False) as outfile:
            plistlib.dump(plistDict, outfile)
            outfileName = outfile.name
            #print('outfile name: {}'.format(outfileName))

        return outfileName
    
        
if __name__ == '__main__':
    app = ClockTalk(CommandLineParser().run())
    app.run()
