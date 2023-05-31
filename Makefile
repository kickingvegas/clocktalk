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

INSTALL_DIR=$(HOME)/bin
EXEC_NAME=clocktalk

$(INSTALL_DIR):
	mkdir $(INSTALL_DIR)

install: $(INSTALL_DIR)
	cp $(EXEC_NAME).py $(INSTALL_DIR)/$(EXEC_NAME)
	chmod uog+x $(INSTALL_DIR)/$(EXEC_NAME)

uninstall: $(HOME)/bin
	rm -f $(INSTALL_DIR)/$(EXEC_NAME)

read: 
	defaults read com.apple.speech.synthesis.general.prefs

