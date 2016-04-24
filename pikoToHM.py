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
from pyowm import OWM

import time
import sys
import logging, logging.handlers


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

PIKO_INTERVAL = 30 # seconds
OWM_INTERVAL = 1800 # seconds
HM_PV_REMAINING_POWER_ID = 12772
HM_PV_STRING_1_POWER_ID = 15241
HM_PV_STRING_2_POWER_ID = 15242
HM_WEATHER_FORECAST_CLOUDS_ID = 20144
HM_WEATHER_CURRENT_TEMPERATURE_ID = 21442
HM_WEATHER_FORECAST_TEMPERATURE_ID = 21443
OWM_API_KEY = 'insert'
OWM_CITY_ID = 2835477

logging.info('Started')
p = Piko(host='http://192.168.178.123')
hm = HM('http://192.168.178.49')
owm = OWM(OWM_API_KEY)
last_weather_update = time.time() - OWM_INTERVAL # - OWM_INTERVAL to update on first run


while(True):
    try:
        # -------------------------------
        # Weather
        now = time.time()
        if (now - last_weather_update) >= OWM_INTERVAL:
            try:

                # Queries the OWM web API for three hours weather forecast for the specified city ID. 
                # A Forecaster object is returned, containing a Forecast instance covering a global streak of five days: 
                # this instance encapsulates Weather objects, with a time interval of three hours one from each other
                logging.debug('Calling: owm.three_hours_forecast_at_id')
                forecast = owm.three_hours_forecast_at_id(OWM_CITY_ID).get_forecast()
                
                # get current weather
                logging.debug('Calling: owm.weather_at_id')
                weather = owm.weather_at_id(OWM_CITY_ID).get_weather()
                
                # set the cloud coverage of the weather to homematic
                # .get_clouds(): Returns the cloud coverage percentage as an int
                logging.debug('Calling: set_state HM_WEATHER_FORECAST_CLOUDS_ID')
                hm.set_state(HM_WEATHER_FORECAST_CLOUDS_ID, weather.get_clouds())
                
                # set the current temperature of the weather to homematic
                # .get_temperature(): Returns a dict with temperature info {'temp': 293.4, 'temp_kf': None, 'temp_max': 297.5, 'temp_min': 290.9}
                hm.set_state(HM_WEATHER_CURRENT_TEMPERATURE_ID, weather.get_temperature(unit="celsius")["temp"])
                
                # set the temperature of the weather in 12 hours to homematic
                # .get(): Lookups up into the Weather items list for the item at the specified index
                # .get_temperature(): Returns a dict with temperature info {'temp': 293.4, 'temp_kf': None, 'temp_max': 297.5, 'temp_min': 290.9}
                hm.set_state(HM_WEATHER_FORECAST_TEMPERATURE_ID, forecast.get(3).get_temperature(unit="celsius")["temp"])
                
                # Update last_weather_update time
                last_weather_update = time.time()
            except: # catch *all* exceptions
                err = sys.exc_info()[0]
                logging.exception('Error on updating weather: {0}'.format(err))
    
    
        # -------------------------------
        # Piko
        # Get values for remaining power calculation
        logging.debug('Calling: get_current_power')
        current_solar_power = p.get_current_power()
        
        logging.debug('Calling: get_consumption_phase_1')
        consumption_phase_1 = p.get_consumption_phase_1()
        
        logging.debug('Calling: get_consumption_phase_2')
        consumption_phase_2 = p.get_consumption_phase_2()
        
        logging.debug('Calling: get_consumption_phase_3')
        consumption_phase_3 = p.get_consumption_phase_3()
        
        # Get values for string 1 power and string 2 power
        logging.debug('Calling: get_string1_current')
        string1Current = p.get_string1_current()
        
        logging.debug('Calling: get_string2_current')
        string2Current = p.get_string2_current()
        
        logging.debug('Calling: get_string1_voltage')
        string1Voltage = p.get_string1_voltage()
        
        logging.debug('Calling: get_string2_voltage')
        string2Voltage = p.get_string2_voltage()
        
        if current_solar_power < 0:
            # Piko is off
            logging.info('Piko is off, going to sleep 10 minutes.')
            # Set state of homematic
            logging.debug('Calling: set_state HM_PV_REMAINING_POWER_ID')
            hm.set_state(HM_PV_REMAINING_POWER_ID, 0)
            
            logging.debug('Calling: set_state HM_PV_STRING_1_POWER_ID')
            hm.set_state(HM_PV_STRING_1_POWER_ID, 0)
            
            logging.debug('Calling: set_state HM_PV_STRING_2_POWER_ID')
            hm.set_state(HM_PV_STRING_2_POWER_ID, 0)
            
            logging.debug('Calling: time.sleep 600')
            time.sleep(600)
            continue
        
        # Calculate remaining power
        logging.debug('Rounding for remaining_power')
        remaining_power = round(current_solar_power - (consumption_phase_1 + consumption_phase_2 + consumption_phase_3))
        if remaining_power < 0:
            remaining_power = 0
            
        # Calculate string 1 power and string 2 power
        string1 = round(string1Current * string1Voltage)
        string2 = round(string2Current * string2Voltage)
        
        # Set state of homematic
        logging.debug('Calling: set_state HM_PV_REMAINING_POWER_ID')
        hm.set_state(HM_PV_REMAINING_POWER_ID, remaining_power)
        
        logging.debug('Calling: set_state HM_PV_STRING_1_POWER_ID')
        hm.set_state(HM_PV_STRING_1_POWER_ID, string1)
        
        logging.debug('Calling: set_state HM_PV_STRING_2_POWER_ID')
        hm.set_state(HM_PV_STRING_2_POWER_ID, string2)
        
        # Sleep
        logging.debug('Calling: time.sleep PIKO_INTERVAL')
        time.sleep(PIKO_INTERVAL)
        
    except KeyboardInterrupt:
        break
    except: # catch *all* exceptions
        err = sys.exc_info()[0]
        logging.exception('Error: {0}'.format(err))
        continue
