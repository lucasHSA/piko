# The MIT License (MIT)
#
# Copyright (c) 2015 Lucas Koegel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import xml.etree.ElementTree as ET
import logging


class HM():
    def __init__(self, host='http://192.168.178.49'):
        self._host = host
        
    def set_state(self, id, value):
        # Change state
        response = requests.get(self._host + "/config/xmlapi/statechange.cgi?ise_id=" + str(id) + "&new_value=" + str(value))
        root = ET.fromstring(response.text)
        
        # Check response
        error = root.find("not_found")
        if error is not None:
            logging.error("Systemvariable was not found. Couldn't set PV-Power.")
            
        success = root.find("changed")
        if success is not None:
            logging.debug("Set systemvariable " + str(id) + " successfully to " + str(value))
        

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    format = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    ch.setFormatter(format)
    logger.addHandler(ch)
    # Get all system variables
    response = requests.get('http://192.168.178.49/config/xmlapi/sysvarlist.cgi')
    print(response.text)
    
    #hm = HM("http://192.168.178.148")
    #hm.set_state(12772, 300)