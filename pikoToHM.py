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

from piko import Piko
from hm import HM

import time
import sys
import logging


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    fh = logging.FileHandler('pikoToHM.log')
    fh.setLevel(logging.INFO)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    ch.setFormatter(format)
    logger.addHandler(ch)
    logger.addHandler(fh)

    logging.info('Started')
    p = Piko(host='http://192.168.178.123')
    hm = HM('http://192.168.178.148')
    INTERVAL = 30 # seconds
    HM_PV_REMAINING_POWER_ID = 12772

    while(True):
        try:
            solar_generator_power = p.get_solar_generator_power()
            consumption_phase_1 = p.get_consumption_phase_1()
            consumption_phase_2 = p.get_consumption_phase_2()
            consumption_phase_3 = p.get_consumption_phase_3()
            remaining_power = solar_generator_power - (consumption_phase_1 + consumption_phase_2 + consumption_phase_3)
            
            if remaining_power < 0:
                remaining_power = 0
            
            # Set state of homematic
            hm.set_state(HM_PV_REMAINING_POWER_ID, remaining_power)

            logging.debug('Set Homematic state of ' + str(HM_PV_REMAINING_POWER_ID) + ' to ' + str(remaining_power))    

        except: # catch *all* exceptions
            logging.error('Error: ', sys.exc_info()[0])

        # Sleep
        time.sleep(INTERVAL)