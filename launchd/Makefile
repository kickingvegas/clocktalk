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

LABEL_PREFIX=com.yummymelon.clocktalk
INSTALL_DIR=$(HOME)/Library/LaunchAgents

.PHONY: plists install load unload clean reinstall status uninstall list

plists: $(LABEL_PREFIX)-start.plist $(LABEL_PREFIX)-stop.plist

$(LABEL_PREFIX)-start.plist:
	./genclocktalkd.py --label $(LABEL_PREFIX)-start \
--time 7:50 \
--period hour \
--volume 0.3 \
--enable \
--execute 

$(LABEL_PREFIX)-stop.plist:
	./genclocktalkd.py --label $(LABEL_PREFIX)-stop \
--time 18:50 \
--period hour \
--volume 0.3 \
--execute

install: plists
	cp -f $(LABEL_PREFIX)-start.plist $(INSTALL_DIR)
	cp -f $(LABEL_PREFIX)-stop.plist $(INSTALL_DIR)

reinstall: clean install unload load

uninstall: unload
	rm -f $(INSTALL_DIR)/$(LABEL_PREFIX)-start.plist
	rm -f $(INSTALL_DIR)/$(LABEL_PREFIX)-stop.plist

load:
	launchctl load $(INSTALL_DIR)/$(LABEL_PREFIX)-start.plist
	launchctl load $(INSTALL_DIR)/$(LABEL_PREFIX)-stop.plist

unload:
	launchctl unload $(INSTALL_DIR)/$(LABEL_PREFIX)-start.plist
	launchctl unload $(INSTALL_DIR)/$(LABEL_PREFIX)-stop.plist

status:
	- launchctl list $(LABEL_PREFIX)-start
	- launchctl list $(LABEL_PREFIX)-stop

list:
	plutil -convert json $(INSTALL_DIR)/$(LABEL_PREFIX)-start.plist -o - | python3 -m json.tool
	plutil -convert json $(INSTALL_DIR)/$(LABEL_PREFIX)-stop.plist -o - | python3 -m json.tool

clean:
	- rm -f $(LABEL_PREFIX)-start.plist $(LABEL_PREFIX)-stop.plist

