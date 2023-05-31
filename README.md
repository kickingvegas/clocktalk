# clocktalk  - Command line utility to configure and enable periodic macOS time announcements

# Summary

`clocktalk` is a command line utility to configure and enable periodic time announcements (usually by the hour) via macOS speech synthesis. Typically this setting is accessed via the macOS GUI **Settings** app which on Ventura 13.4+ is located at *Control Center > Clock > Clock Options > Announce the time*. 

Because `clocktalk` is a command line utility, it can be automated using `launchd` so that announcing the time is scheduled for different times of the day.

`clocktalk` internally uses the `defaults` command line utility to change the system state of the periodic time announcement.

# Usage

```Shell
usage: clocktalk [-h] [-v] [-p {hour,half,quarter}] [-r] [-e] [-V VOLUME] [-x]

Command line utility to configure and enable periodic macOS time announcements.

options:
  -h, --help            show this help message and exit
  -v, --version         print version information and exit
  -p {hour,half,quarter}, --period {hour,half,quarter}
                        period to annouce time (default hour)
  -r, --read            read current configuration (all other arguments ignored)
  -e, --enable          enable periodic time announcements (default is disabled if not present)
  -V VOLUME, --volume VOLUME
                        set volume from 0.0 to 1.0 (default 0.5 if not present)
  -x, --execute         when present, execute the acutal `defaults` command

This is a wrapper script around the command line tool `defaults` to configure the domain `com.apple.speech.synthesis.general.prefs`.
```

# Install

Installation of `clocktalk` is via a `Makefile` target `install`. It is invoked as shown below.

```Shell
$ make install
```

In the `Makefile` the `INSTALL_DIR` is set to `$(HOME)/bin` which will be created if it does not already exist. `$(HOME)/bin` should also be in your `PATH` environment variable. If you wish `INSTALL_DIR` to be different, the `INSTALL_DIR` in the `Makefile` to your preference before running `make install`.

# Running `clocktalk`

To turn on the clock announcements so that they are spoken at the top of the hour run the following command:

```Shell
$ clocktalk --enable --execute
```

Alternately you can use the short argument flags and type `clocktalk -ex`. 

To turn off the clock announcements:

```Shell
$ clocktalk --execute
```

To view the current state of the general preferences for the speech synthesizer, 

```Shell
$ clocktalk --read
```
Note that just invoking `clocktalk` alone will also default to reading the speech synthesizer general preferences.


# License

Copyright © Charles Y. Choi

Licensed under the Apache License, Version 2.0 (the “License”); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

