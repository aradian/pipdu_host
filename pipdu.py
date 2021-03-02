#!/usr/bin/python

import metercontroller as mc
import relayboard as r
import webinterface as w
import signal
import logging
import sdnotify

data_path = '/var/local/pipdu-data/'
run_ok = True

logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%s',
        filename = data_path + 'log/activity.log',
        filemode = 'w')
console = logging.StreamHandler()
logging.getLogger('').addHandler(console)

logging.info('Start')

r.initialize()
r.set_relays([1,2,3,4,5,6], True)

logging.info('Initialized relay controller')

mcontroller = mc.MeterController(data_path + 'meter_data/main.rrd')

logging.info('Initialized meter controller')

def shutdown_handler(signum, frame):
    logging.info('Got signal: ' + str(signum))
    run_ok = False
    mcontroller.stop_recording()

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGHUP, shutdown_handler)
signal.signal(signal.SIGUSR1, shutdown_handler)
signal.signal(signal.SIGUSR2, shutdown_handler)

mcontroller.start_recording()

logging.info('Recording started')

w.WebInterface.data_path = data_path
w.WebInterface.meter_ctrl = mcontroller
w.WebInterface.relay_state = [True, True, True, True, True, True]

webserver = w.http.HTTPServer(('127.0.0.1', 8081), w.WebInterface)

logging.info('HTTP server configured, starting')

sdnotify.SystemdNotifier().notify('READY=1')

try:
    while run_ok:
        webserver.handle_request()
except KeyboardInterrupt:
    logging.info('CTRL-C')

mcontroller.stop_recording()

logging.info('Recording stopped')
logging.info('Exiting')

