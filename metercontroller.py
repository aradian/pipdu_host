
import atm90e36a.device as a
import meterconfig as mconf
import os
import time
from time import sleep
import pyrrd.rrd as rrd
import threading
import logging

class MeterController:
    meter1 = a.ATM90E36A( \
        mconf._M1_SPI_BUS, \
        mconf._M1_SPI_DEV, \
        mconf._M1_GPIO_PIN_PM0, \
        mconf._M1_GPIO_PIN_PM1, \
        mconf._M1_GPIO_PIN_IRQ0)
    meter1_lock = threading.Lock()

    meter2 = a.ATM90E36A( \
        mconf._M2_SPI_BUS, \
        mconf._M2_SPI_DEV, \
        mconf._M2_GPIO_PIN_PM0, \
        mconf._M2_GPIO_PIN_PM1, \
        mconf._M2_GPIO_PIN_IRQ0)
    meter2_lock = threading.Lock()

    logger = logging.getLogger('meterctrl')

    def __init__(self, rrd_path, rec_interval = 5):
        with self.meter1_lock:
            self.meter1.initialize()
            self.meter1.set_config_data(mconf._M1_REG_CONFIG)

        with self.meter2_lock:
            self.meter2.initialize()
            self.meter2.set_config_data(mconf._M2_REG_CONFIG)

        self._recording_path = rrd_path
        self._recording_db = None
        self._recording_db_lock = threading.Lock()
        self._last_dataset = []

        self._recording_interval = rec_interval
        self._recording_thread = threading.Thread( \
                target = self._record_loop, \
                name = "recording_thread")
        self._recording_stop_event = threading.Event()

        self.logger.debug('Initialized')

    def __del__(self):
        self.stop_recording()
        with self.meter1_lock, self.meter2_lock:
            self.meter1.set_power_mode(a.flags.PM_Idle)
            self.meter2.set_power_mode(a.flags.PM_Idle)

    def start_recording(self):
        self.logger.info('Start recording')
        if self._recording_thread.is_alive():
            return
        self._record_setup()
        self._recording_stop_event.clear()

        with self.meter1_lock, self.meter2_lock:
            self.meter1.set_power_mode(a.flags.PM_Normal)
            self.meter2.set_power_mode(a.flags.PM_Normal)
            sleep(0.01)
            self.meter1.configure()
            self.meter2.configure()

        self._recording_thread.start()

    def stop_recording(self):
        self.logger.info('Stop recording')
        if not self._recording_thread.is_alive():
            return
        self._recording_stop_event.set()
        self._recording_thread.join()

        with self.meter1_lock, self.meter2_lock:
            self.meter1.set_power_mode(a.flags.PM_Idle)
            self.meter2.set_power_mode(a.flags.PM_Idle)

    def getclear_energy_data(self):
        return {
                '1': {
                    '1': {
                        'energy_active_forward_kWh': self.meter1.getclear_APEnergy_A(),
                        'energy_active_reverse_kWh': self.meter1.getclear_ANEnergy_A(),
                        'energy_reactive_forward_kWh': self.meter1.getclear_RPEnergy_A(),
                        'energy_reactive_reverse_kWh': self.meter1.getclear_RNEnergy_A(),
                        },
                    '2': {
                        'energy_active_forward_kWh': self.meter1.getclear_APEnergy_B(),
                        'energy_active_reverse_kWh': self.meter1.getclear_ANEnergy_B(),
                        'energy_reactive_forward_kWh': self.meter1.getclear_RPEnergy_B(),
                        'energy_reactive_reverse_kWh': self.meter1.getclear_RNEnergy_B(),
                        },
                    '3': {
                        'energy_active_forward_kWh': self.meter1.getclear_APEnergy_C(),
                        'energy_active_reverse_kWh': self.meter1.getclear_ANEnergy_C(),
                        'energy_reactive_forward_kWh': self.meter1.getclear_RPEnergy_C(),
                        'energy_reactive_reverse_kWh': self.meter1.getclear_RNEnergy_C(),
                        },
                    },
                '2': {
                    '4': {
                        'energy_active_forward_kWh': self.meter2.getclear_APEnergy_A(),
                        'energy_active_reverse_kWh': self.meter2.getclear_ANEnergy_A(),
                        'energy_reactive_forward_kWh': self.meter2.getclear_RPEnergy_A(),
                        'energy_reactive_reverse_kWh': self.meter2.getclear_RNEnergy_A(),
                        },
                    '5': {
                        'energy_active_forward_kWh': self.meter2.getclear_APEnergy_B(),
                        'energy_active_reverse_kWh': self.meter2.getclear_ANEnergy_B(),
                        'energy_reactive_forward_kWh': self.meter2.getclear_RPEnergy_B(),
                        'energy_reactive_reverse_kWh': self.meter2.getclear_RNEnergy_B(),
                        },
                    '6': {
                        'energy_active_forward_kWh': self.meter2.getclear_APEnergy_C(),
                        'energy_active_reverse_kWh': self.meter2.getclear_ANEnergy_C(),
                        'energy_reactive_forward_kWh': self.meter2.getclear_RPEnergy_C(),
                        'energy_reactive_reverse_kWh': self.meter2.getclear_RNEnergy_C(),
                        },
                    },
                }

    def get_last_data(self):
        with self._recording_db_lock:
            export_data = list(self._last_dataset)
        return export_data

    def get_recorded_data(self, start_time, end_time):
        self.logger.info('Get recorded data: ' + str(start_time) + ' thru ' + str(end_time))
        with self._recording_db_lock:
            export_data = self._recording_db.fetch( \
                    start = start_time, \
                    end = end_time, \
                    returnStyle = 'ds')
        return export_data

    def _record_setup(self):
        data_sources = [ \
                # meter 1 sources
                rrd.DataSource( \
                    dsName = 'source1_voltage', \
                    dsType = 'GAUGE', \
                    heartbeat = 1800, \
                    minval = 0, \
                    maxval = 300), \
                # CH 1-3 current
                rrd.DataSource(dsName = 'ch1_I', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch2_I', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch3_I', dsType = 'GAUGE', heartbeat = 12), \
                # CH 1-3 active power
                rrd.DataSource(dsName = 'ch1_P', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch2_P', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch3_P', dsType = 'GAUGE', heartbeat = 12), \
                # CH 1-3 reactive power
                rrd.DataSource(dsName = 'ch1_Q', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch2_Q', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch3_Q', dsType = 'GAUGE', heartbeat = 12), \
                # CH 1-3 apparent power
                rrd.DataSource(dsName = 'ch1_S', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch2_S', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch3_S', dsType = 'GAUGE', heartbeat = 12), \
                # CH 1-3 power factor
                rrd.DataSource(dsName = 'ch1_PF', dsType = 'GAUGE', heartbeat = 12, minval = -1.0, maxval = 1.0), \
                rrd.DataSource(dsName = 'ch2_PF', dsType = 'GAUGE', heartbeat = 12, minval = -1.0, maxval = 1.0), \
                rrd.DataSource(dsName = 'ch3_PF', dsType = 'GAUGE', heartbeat = 12, minval = -1.0, maxval = 1.0), \

                # meter 2 sources
                rrd.DataSource( \
                    dsName = 'source2_voltage', \
                    dsType = 'GAUGE', \
                    heartbeat = 1800, \
                    minval = 0, \
                    maxval = 300), \
                # CH 4-6 current
                rrd.DataSource(dsName = 'ch4_I', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch5_I', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch6_I', dsType = 'GAUGE', heartbeat = 12), \
                # CH 4-6 active power
                rrd.DataSource(dsName = 'ch4_P', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch5_P', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch6_P', dsType = 'GAUGE', heartbeat = 12), \
                # CH 4-6 reactive power
                rrd.DataSource(dsName = 'ch4_Q', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch5_Q', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch6_Q', dsType = 'GAUGE', heartbeat = 12), \
                # CH 4-6 apparent power
                rrd.DataSource(dsName = 'ch4_S', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch5_S', dsType = 'GAUGE', heartbeat = 12), \
                rrd.DataSource(dsName = 'ch6_S', dsType = 'GAUGE', heartbeat = 12), \
                # CH 4-6 power factor
                rrd.DataSource(dsName = 'ch4_PF', dsType = 'GAUGE', heartbeat = 12, minval = -1.0, maxval = 1.0), \
                rrd.DataSource(dsName = 'ch5_PF', dsType = 'GAUGE', heartbeat = 12, minval = -1.0, maxval = 1.0), \
                rrd.DataSource(dsName = 'ch6_PF', dsType = 'GAUGE', heartbeat = 12, minval = -1.0, maxval = 1.0), \

                rrd.DataSource(dsName = 'temperature', dsType = 'GAUGE', heartbeat = 12),
                rrd.DataSource(dsName = 'frequency', dsType = 'GAUGE', heartbeat = 12, minval = 0.0),
                rrd.DataSource(dsName = 'measurement_time', dsType = 'GAUGE', heartbeat = 12, minval = 0.0),
                ]
        data_archives = [ \
                # step 5s, row 1d
                rrd.RRA( \
                    cf = 'AVERAGE', \
                    xff = 0.5, \
                    steps = 1, \
                    rows = 17280), \
                # step 1m, row 2d
                rrd.RRA( \
                    cf = 'AVERAGE', \
                    xff = 0.5, \
                    steps = 12, \
                    rows = 2880), \
                # step 1h, row 10d
                rrd.RRA( \
                    cf = 'AVERAGE', \
                    xff = 0.5, \
                    steps = 720, \
                    rows = 240), \
                ]

        with self._recording_db_lock:
            if os.path.isfile(self._recording_path):
                os.unlink(self._recording_path)

            self._recording_db = rrd.RRD( \
                    self._recording_path, \
                    ds = data_sources, \
                    rra = data_archives, \
                    start = 'now', \
                    step = 5)
            self._recording_db.create()

    def _record_loop(self):
        while True:
            with self.meter1_lock, self.meter2_lock:
                #self.meter1.set_power_mode(a.flags.PM_Normal)
                #self.meter2.set_power_mode(a.flags.PM_Normal)
                #sleep(0.01)
                mt_start = time.time()
                #self.meter1.configure()
                #self.meter2.configure()
                dataset = [ int(time.time()),
                        self.meter1.get_Vrms_A(),
                        self.meter1.get_Irms_A(), self.meter1.get_Irms_B(), self.meter1.get_Irms_C(),
                        self.meter1.get_Pavg_A(), self.meter1.get_Pavg_B(), self.meter1.get_Pavg_C(),
                        self.meter1.get_Qavg_A(), self.meter1.get_Qavg_B(), self.meter1.get_Qavg_C(),
                        self.meter1.get_Savg_A(), self.meter1.get_Savg_B(), self.meter1.get_Savg_C(),
                        self.meter1.get_PFavg_A(), self.meter1.get_PFavg_B(), self.meter1.get_PFavg_C(),
                        self.meter2.get_Vrms_A(),
                        self.meter2.get_Irms_A(), self.meter2.get_Irms_B(), self.meter2.get_Irms_C(),
                        self.meter2.get_Pavg_A(), self.meter2.get_Pavg_B(), self.meter2.get_Pavg_C(),
                        self.meter2.get_Qavg_A(), self.meter2.get_Qavg_B(), self.meter2.get_Qavg_C(),
                        self.meter2.get_Savg_A(), self.meter2.get_Savg_B(), self.meter2.get_Savg_C(),
                        self.meter2.get_PFavg_A(), self.meter2.get_PFavg_B(), self.meter2.get_PFavg_C(),
                        self.meter1.get_Temperature(),
                        self.meter1.get_Frequency(),
                        ]
                mt_end = time.time()
                #self.meter1.set_power_mode(a.flags.PM_Idle)
                #self.meter2.set_power_mode(a.flags.PM_Idle)

            dataset.append(mt_end - mt_start)

            with self._recording_db_lock:
                self._last_dataset = dataset
                self._recording_db.bufferValue(*dataset)
                self._recording_db.update()

            if self._recording_stop_event.wait(self._recording_interval):
                break

