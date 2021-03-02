
from time import sleep
from array import array
import spidev as spi
import RPi.GPIO as gpio
import registers as reg
import flags
from utils import *
import logging

class ATM90E36A:
    _spi_max_speed = 1000

    def __init__(self, spi_bus, spi_dev, pin_pm0, pin_pm1, pin_irq0):
        self._spi_bus = spi_bus
        self._spi_dev = spi_dev
        self._pin_pm0 = pin_pm0
        self._pin_pm1 = pin_pm1
        self._pin_irq0 = pin_irq0
        self._spi = spi.SpiDev()
        self._reg_config = {}
        self._logger = logging.getLogger('device_' + str(spi_bus) + '.' + str(spi_dev))

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        self.set_power_mode(flags.PM_Idle)
        self._spi.close()

    def initialize(self):
        self._logger.debug('Initialize')

        gpio.setmode(gpio.BOARD)
        gpio.setup(self._pin_irq0, gpio.IN)
        gpio.setup([self._pin_pm0, self._pin_pm1], gpio.OUT)

        self.set_power_mode(flags.PM_Idle)

        self._spi.open(self._spi_bus, self._spi_dev)
        self._spi.max_speed_hz = self._spi_max_speed

    def set_power_mode(self, mode):
        self._logger.debug('Set power mode ' + str(mode))

        gpio.output([self._pin_pm0, self._pin_pm1], gpio.LOW)
        sleep(0.125)
        if mode == flags.PM_Normal:
            gpio.output([self._pin_pm0, self._pin_pm1], gpio.HIGH)
        elif mode & 0b01:
            gpio.output(self._pin_pm0, gpio.HIGH)
        elif mode & 0b10:
            gpio.output(self._pin_pm1, gpio.HIGH)

    def read(self, addr):
        send_seq = uint_to_bytevec(addr, 2) + [0x0, 0x0]
        send_seq[0] |= 0x80
        return self._spi.xfer(send_seq)[2:4]

    def read_uint(self, addr):
        return bytevec_to_uint(self.read(addr))

    def read_uint24(self, addrs):
        return bytevec_to_uint(self.read(addrs[0])) + \
                self.read(addrs[1])[0] * (1.0 / 0x100)

    def read_cint24(self, addrs):
        data = self.read_group(addrs)
        sign = 1
        if data[0] & 0x80:
            data = map(lambda (x): x ^ 0xff, data) # ~ uses python's infinite bits
            sign = -1
        return (bytevec_to_uint(data[0:2]) + \
                data[2] * (1.0 / 0x100)) * sign

    def read_cint16(self, addr):
        data = self.read(addr)
        sign = 1
        if data[0] & 0x80:
            data = map(lambda (x): x ^ 0xff, data) # ~ uses python's infinite bits
            sign = -1
        return bytevec_to_uint(data) * sign

    def read_group(self, addrs):
        result = []
        for addr in addrs:
            result += self.read(addr)
        return result

    def write(self, addr, bytevec):
        self._spi.xfer(uint_to_bytevec(addr, 2) + bytevec)

    def write_uint(self, addr, data):
        self.write(addr, uint_to_bytevec(data, 2))

    def write_group(self, addrs, bytelist):
        for addr in addrs:
            self.write(addr, bytelist[0:2])
            del bytelist[0:2]

    def get_Vrms_A(self):
        return self.read_uint24([reg.UrmsA, reg.UrmsALSB]) * 0.01
    def get_Vrms_B(self):
        return self.read_uint24([reg.UrmsB, reg.UrmsBLSB]) * 0.01
    def get_Vrms_C(self):
        return self.read_uint24([reg.UrmsC, reg.UrmsCLSB]) * 0.01

    def get_Irms_A(self):
        return self.read_uint24([reg.IrmsA, reg.IrmsALSB]) * 0.001
    def get_Irms_B(self):
        return self.read_uint24([reg.IrmsB, reg.IrmsBLSB]) * 0.001
    def get_Irms_C(self):
        return self.read_uint24([reg.IrmsC, reg.IrmsCLSB]) * 0.001

    def get_Pavg_A(self):
        return self.read_cint24([reg.PmeanA, reg.PmeanALSB])
    def get_Qavg_A(self):
        return self.read_cint24([reg.QmeanA, reg.QmeanALSB])
    def get_Savg_A(self):
        return self.read_cint24([reg.SmeanA, reg.SmeanALSB])
    def get_Pavg_B(self):
        return self.read_cint24([reg.PmeanB, reg.PmeanBLSB])
    def get_Qavg_B(self):
        return self.read_cint24([reg.QmeanB, reg.QmeanBLSB])
    def get_Savg_B(self):
        return self.read_cint24([reg.SmeanB, reg.SmeanBLSB])
    def get_Pavg_C(self):
        return self.read_cint24([reg.PmeanC, reg.PmeanCLSB])
    def get_Qavg_C(self):
        return self.read_cint24([reg.QmeanC, reg.QmeanCLSB])
    def get_Savg_C(self):
        return self.read_cint24([reg.SmeanC, reg.SmeanCLSB])

    def get_PFavg_A(self):
        return self.read_cint16(reg.PFmeanA) * 0.001
    def get_PFavg_B(self):
        return self.read_cint16(reg.PFmeanB) * 0.001
    def get_PFavg_C(self):
        return self.read_cint16(reg.PFmeanC) * 0.001

    def getclear_APEnergy_A(self):
        return self.read_uint(reg.APenergyA) * 0.1 / self._reg_config['MeterConstant']
    def getclear_APEnergy_B(self):
        return self.read_uint(reg.APenergyB) * 0.1 / self._reg_config['MeterConstant']
    def getclear_APEnergy_C(self):
        return self.read_uint(reg.APenergyC) * 0.1 / self._reg_config['MeterConstant']
    def getclear_ANEnergy_A(self):
        return self.read_uint(reg.ANenergyA) * 0.1 / self._reg_config['MeterConstant']
    def getclear_ANEnergy_B(self):
        return self.read_uint(reg.ANenergyB) * 0.1 / self._reg_config['MeterConstant']
    def getclear_ANEnergy_C(self):
        return self.read_uint(reg.ANenergyC) * 0.1 / self._reg_config['MeterConstant']
    def getclear_RPEnergy_A(self):
        return self.read_uint(reg.RPenergyA) * 0.1 / self._reg_config['MeterConstant']
    def getclear_RPEnergy_B(self):
        return self.read_uint(reg.RPenergyB) * 0.1 / self._reg_config['MeterConstant']
    def getclear_RPEnergy_C(self):
        return self.read_uint(reg.RPenergyC) * 0.1 / self._reg_config['MeterConstant']
    def getclear_RNEnergy_A(self):
        return self.read_uint(reg.RNenergyA) * 0.1 / self._reg_config['MeterConstant']
    def getclear_RNEnergy_B(self):
        return self.read_uint(reg.RNenergyB) * 0.1 / self._reg_config['MeterConstant']
    def getclear_RNEnergy_C(self):
        return self.read_uint(reg.RNenergyC) * 0.1 / self._reg_config['MeterConstant']

    def get_THDN_VA(self):
        return self.read_uint(reg.THDNUA) * 0.0001
    def get_THDN_VB(self):
        return self.read_uint(reg.THDNUB) * 0.0001
    def get_THDN_VC(self):
        return self.read_uint(reg.THDNUC) * 0.0001
    def get_THDN_IA(self):
        return self.read_uint(reg.THDNIA) * 0.0001
    def get_THDN_IB(self):
        return self.read_uint(reg.THDNIB) * 0.0001
    def get_THDN_IC(self):
        return self.read_uint(reg.THDNIC) * 0.0001

    def get_Frequency(self):
        return self.read_uint(reg.Freq) * 0.01

    def get_Temperature(self):
        return self.read_uint(reg.Temp)

    def _calc_harm_pct(self, addr):
        return self.read_uint(addr) / 16384.0

    def run_DFT(self):
        self.write_uint(reg.DFTCtrl, flags.DFTCtrl_Enable)
        while self.read_uint(reg.DFTCtrl):
            sleep(0.1)

    def get_HarmDFT_VA(self):
        return map(self._calc_harm_pct, reg.HarmRatiosVA)
    def get_FundComp_VA(self):
        return (self.read_uint(reg.FundCompValVA) * 3.2656) / (100 * 2 ** self._reg_config['DFTVoltageScale'])

    def _verify_cs(self, cs_reg):
        self.write(cs_reg, self.read(cs_reg))

    def _try_start(self, startup_reg_address, cs_flag):
        self.write_uint(startup_reg_address, flags.StartupVal_Operation)
        status_val = self.read_uint(startup_reg_address)
        if status_val != flags.StartupVal_Operation:
            self._logger.error("Failed to set operation mode for start reg: %(addr)#02x\n" % \
                    {"addr": startup_reg_address})
            return False
        if (self.read_uint(reg.SysStatus0) & cs_flag) != 0:
            self._logger.error("Checksum failed associated with start reg: %(addr)#02x\n" % \
                    {"addr": startup_reg_address})
            return False
        return True

    def set_config_data(self, data):
        self._reg_config.update(data)

    def configure(self, operation=True):
        self.write_uint(reg.ConfigStart, flags.StartupVal_Calibration)
        self._config_pl_const()
        self._config_metering_method()
        self._config_pga_gain()
        self._config_temp_sensor()
        if operation:
            self._verify_cs(reg.CS0)
            self._try_start(reg.ConfigStart, flags.SysStatus0_CS0Err)

        self.write_uint(reg.CalStart, flags.StartupVal_Calibration)
        self.write_uint(reg.HarmStart, flags.StartupVal_Calibration)
        self.write_uint(reg.AdjStart, flags.StartupVal_Calibration)
        self._config_offsets()
        self._config_VI_measurement()
        self._config_energy_metering()
        self._config_fund_energy_metering()
        if operation:
            self._verify_cs(reg.CS1)
            self._try_start(reg.CalStart, flags.SysStatus0_CS1Err)
            self._verify_cs(reg.CS2)
            self._try_start(reg.HarmStart, flags.SysStatus0_CS2Err)
            self._verify_cs(reg.CS3)
            self._try_start(reg.AdjStart, flags.SysStatus0_CS3Err)
        self._config_dft()

    def _write_checksums(self):
        self.write(reg.CS0, self.read(reg.CS0))
        self.write(reg.CS1, self.read(reg.CS1))
        self.write(reg.CS2, self.read(reg.CS2))
        self.write(reg.CS3, self.read(reg.CS3))

    def _config_pl_const(self):
        self.write_group([reg.PLconstH, reg.PLconstL], \
                uint_to_bytevec(int(450000000000 / self._reg_config['MeterConstant']), 4))

    def _config_metering_method(self):
        self.write_uint(reg.MMode0, \
                flags.MMode0_Freq60Hz | \
                flags.MMode0_CF2varh | \
                flags.MMode0_EnPA | \
                flags.MMode0_EnPB | \
                flags.MMode0_EnPC)

    def _config_pga_gain(self):
        self.write_uint(reg.MMode1, \
                flags.MMode1_DPGA_GAIN_1 | \
                flags.MMode1_PGA_GAIN_V1_1x | \
                flags.MMode1_PGA_GAIN_V2_1x | \
                flags.MMode1_PGA_GAIN_V3_1x | \
                flags.MMode1_PGA_GAIN_I1_1x | \
                flags.MMode1_PGA_GAIN_I2_1x | \
                flags.MMode1_PGA_GAIN_I3_1x | \
                flags.MMode1_PGA_GAIN_I4_1x)

    def _config_temp_sensor(self):
        self.write_uint(reg.TempSensorConfig1, flags.TempSensorConfigStart)
        self.write_uint(reg.TempSensorConfig2, flags.TempSensorConfigValA)
        self.write_uint(reg.TempSensorConfig3, flags.TempSensorConfigValB)
        self.write_uint(reg.TempSensorConfig1, flags.TempSensorConfigEnd)

    def _config_dft(self):
        self.write_uint(reg.DFTConfig, \
                (2 ** self._reg_config['DFTVoltageScale']) << flags.DFTConfig_VScaleA_Shift | \
                (2 ** self._reg_config['DFTVoltageScale']) << flags.DFTConfig_VScaleB_Shift | \
                (2 ** self._reg_config['DFTVoltageScale']) << flags.DFTConfig_VScaleC_Shift | \
                (2 ** self._reg_config['DFTCurrentScale']) << flags.DFTConfig_IScaleA_Shift | \
                (2 ** self._reg_config['DFTCurrentScale']) << flags.DFTConfig_IScaleB_Shift | \
                (2 ** self._reg_config['DFTCurrentScale']) << flags.DFTConfig_IScaleC_Shift)

    def _calc_VI_offset(self, addrs):
        samples = array('L')
        for i in range(0,5):
            samples.append(bytevec_to_uint(self.read_group(addrs)))
            sleep(0.1)
        sample_avg = int(sum(samples) / 5)
        return -(sample_avg >> 7) & 0xffff

    def _calc_PQ_offset(self, addrs):
        samples = array('L')
        for i in range(0,5):
            samples.append(bytevec_to_uint(self.read_group(addrs)))
            sleep(0.1)
        sample_avg = int(sum(samples) / 5 * 100000 / 65536)
        return -(sample_avg >> 8) & 0xffff

    def _config_offsets(self):
        self.write_uint(reg.UoffsetA, self._reg_config['UoffsetA'])
        self.write_uint(reg.UoffsetB, self._reg_config['UoffsetB'])
        self.write_uint(reg.UoffsetC, self._reg_config['UoffsetC'])

        self.write_uint(reg.IoffsetA, self._reg_config['IoffsetA'])
        self.write_uint(reg.IoffsetB, self._reg_config['IoffsetB'])
        self.write_uint(reg.IoffsetC, self._reg_config['IoffsetC'])
        self.write_uint(reg.IoffsetN, self._reg_config['IoffsetN'])

        self.write_uint(reg.PoffsetA, self._reg_config['PoffsetA'])
        self.write_uint(reg.QoffsetA, self._reg_config['QoffsetA'])
        self.write_uint(reg.PoffsetB, self._reg_config['PoffsetB'])
        self.write_uint(reg.QoffsetB, self._reg_config['QoffsetB'])
        self.write_uint(reg.PoffsetC, self._reg_config['PoffsetC'])
        self.write_uint(reg.QoffsetC, self._reg_config['QoffsetC'])

        self.write_uint(reg.PoffsetAF, self._reg_config['PoffsetAF'])
        self.write_uint(reg.PoffsetBF, self._reg_config['PoffsetBF'])
        self.write_uint(reg.PoffsetCF, self._reg_config['PoffsetCF'])

    def _config_VI_measurement(self):
        self.write_uint(reg.UgainA, self._reg_config['UgainA'])
        self.write_uint(reg.UgainB, self._reg_config['UgainB'])
        self.write_uint(reg.UgainC, self._reg_config['UgainC'])

        self.write_uint(reg.IgainA, self._reg_config['IgainA'])
        self.write_uint(reg.IgainB, self._reg_config['IgainB'])
        self.write_uint(reg.IgainC, self._reg_config['IgainC'])
        self.write_uint(reg.IgainN, self._reg_config['IgainN'])

    def _config_energy_metering(self):
        self.write_uint(reg.GainA, self._reg_config['GainA'])
        self.write_uint(reg.PhiA, self._reg_config['PhiA'])
        self.write_uint(reg.GainB, self._reg_config['GainB'])
        self.write_uint(reg.PhiB, self._reg_config['PhiB'])
        self.write_uint(reg.GainC, self._reg_config['GainC'])
        self.write_uint(reg.PhiC, self._reg_config['PhiC'])

    def _config_fund_energy_metering(self):
        return

