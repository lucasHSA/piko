﻿# The MIT License (MIT)
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

from piko import Piko
from hm import HM

import time
import sys
import logging, logging.handlers


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh = logging.handlers.RotatingFileHandler('/home/pi/Desktop/piko/pikoToHM.log', maxBytes=1024*1024*512, backupCount=2)
    fh.setLevel(logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(format)
    fh.setFormatter(format)
    logger.addHandler(ch)
    logger.addHandler(fh)

    logging.info('Started')
    p = Piko(host='http://192.168.178.123')
    hm = HM('http://192.168.178.49')
    INTERVAL = 30 # seconds
    HM_PV_REMAINING_POWER_ID = 12772
    HM_PV_STRING_1_POWER_ID = 15241
    HM_PV_STRING_2_POWER_ID = 15242

    while(True):
        try:
            # Get values for remaining power calculation
            current_solar_power = p.get_current_power()
            consumption_phase_1 = p.get_consumption_phase_1()
            consumption_phase_2 = p.get_consumption_phase_2()
            consumption_phase_3 = p.get_consumption_phase_3()
            
            # Get values for string 1 power and string 2 power
            string1Current = p.get_string1_current()
            string2Current = p.get_string2_current()
            string1Voltage = p.get_string1_voltage()
            string2Voltage = p.get_string2_voltage()
            
            if current_solar_power < 0:
                # Piko is off
                logging.info('Piko is off, going to sleep 10 minutes.')
                # Set state of homematic
                hm.set_state(HM_PV_REMAINING_POWER_ID, 0)
                hm.set_state(HM_PV_STRING_1_POWER_ID, 0)
                hm.set_state(HM_PV_STRING_2_POWER_ID, 0)
                time.sleep(600)
                continue
            
            # Calculate remaining power
            remaining_power = round(current_solar_power - (consumption_phase_1 + consumption_phase_2 + consumption_phase_3))
            if remaining_power < 0:
                remaining_power = 0
                
            # Calculate string 1 power and string 2 power
            string1 = round(string1Current * string1Voltage)
            string2 = round(string2Current * string2Voltage)
            
            # Set state of homematic
            hm.set_state(HM_PV_REMAINING_POWER_ID, remaining_power)
            hm.set_state(HM_PV_STRING_1_POWER_ID, string1)
            hm.set_state(HM_PV_STRING_2_POWER_ID, string2)
            
            # Sleep
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            break
        except: # catch *all* exceptions
            logging.exception('Error')