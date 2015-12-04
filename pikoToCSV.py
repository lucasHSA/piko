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

from datetime import datetime

import csv
import time
import sys
import os.path
import logging, logging.handlers


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    fh = logging.handlers.RotatingFileHandler('pikoToCSV.log', maxBytes=1024*1024*512, backupCount=2)
    fh.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    ch.setFormatter(format)
    logger.addHandler(ch)
    logger.addHandler(fh)

    logging.info('Started')
    p = Piko(host='http://192.168.178.123')
    FIELDNAMES = ['zeit', 'ost', 'west']
    INTERVAL = 30 # seconds

    while(True):
        try:
            string1Current = p.get_string1_current()
            string2Current = p.get_string2_current()
            string1Voltage = p.get_string1_voltage()
            string2Voltage = p.get_string2_voltage()

            if (string1Current < 0 or string2Current < 0 or string1Voltage < 0 or string2Voltage < 0):
                # Piko is off
                logging.info('Piko is off, going to sleep 10 minutes.')
                time.sleep(600)
                continue

            # Calculate power
            string1 = round(string1Current * string1Voltage)
            string2 = round(string2Current * string2Voltage)
            today = datetime.now()

            fileName = 'piko-' + today.strftime('%d-%m-%Y') + '.csv'

            if (not os.path.isfile(fileName)):
                # New File -> write Headers
                logging.info('Creating new file... ' + fileName)
                with open(fileName, 'w') as newFile:
                    newFileWriter = csv.DictWriter(newFile, fieldnames=FIELDNAMES)
                    newFileWriter.writeheader()

            with open(fileName, 'a') as csvfile:
                # Existing file -> write piko values
                logging.info('Writing to file ... ' + fileName)
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                writer.writerow({'zeit': today.strftime('%X'), 'ost': string1, 'west': string2})

        except: # catch *all* exceptions
            logging.info("Error:", sys.exc_info()[0])

        # Sleep
        time.sleep(INTERVAL)