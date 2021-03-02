#       Status and Special Register
SoftReset 	= 0x00
SysStatus0 	= 0x01
SysStatus1 	= 0x02
FuncEn0  	= 0x03
FuncEn1  	= 0x04
ZXConfig 	= 0x07
SagTh    	= 0x08
PhaseLossTh 	= 0x09
INWarnTh0 	= 0x0A
INWarnTh1 	= 0x0B
THDNUTh  	= 0x0C
THDNITh  	= 0x0D
DMACtrl  	= 0x0E
LastSPIData 	= 0x0F

#	Low Power Mode Register 
DetectCtrl 	= 0x10
DetectTh1 	= 0x11
DetectTh2 	= 0x12
DetectTh3 	= 0x13
PMOffsetA 	= 0x14
PMOffsetB 	= 0x15
PMOffsetC 	= 0x16
PMPGA    	= 0x17
PMIrmsA  	= 0x18
PMIrmsB  	= 0x19
PMIrmsC  	= 0x1A
PMConfig 	= 0x1B
PMAvgSamples 	= 0x1C
PMIrmsLSB 	= 0x1D

#	Configuration Registers
ConfigStart 	= 0x30
PLconstH 	= 0x31
PLconstL 	= 0x32
MMode0  	= 0x33
MMode1  	= 0x34
PStartTh 	= 0x35
QStartTh 	= 0x36
SStartTh 	= 0x37
PPhaseTh	= 0x38
QPhaseTh 	= 0x39
SPhaseTh 	= 0x3A
CS0     	= 0x3B

#	Calibration Registers 
CalStart 	= 0x40
PoffsetA 	= 0x41
QoffsetA 	= 0x42
PoffsetB 	= 0x43
QoffsetB 	= 0x44
PoffsetC 	= 0x45
QoffsetC	= 0x46
GainA 	= 0x47
PhiA 	= 0x48
GainB 	= 0x49
PhiB 	= 0x4A
GainC 	= 0x4B
PhiC 	= 0x4C
CS1  	= 0x4D

#	Fundamental/Harmonic Energy Calibration regis ters 
HarmStart 	= 0x50
PoffsetAF 	= 0x51
PoffsetBF 	= 0x52
PoffsetCF 	= 0x53
PgainAF 	= 0x54
PgainBF 	= 0x55
PgainCF 	= 0x56
CS2   	= 0x57

#	Measurement Calibration 
AdjStart 	= 0x60
UgainA 	= 0x61
IgainA 	= 0x62
UoffsetA 	= 0x63
IoffsetA 	= 0x64
UgainB 	= 0x65
IgainB 	= 0x66
UoffsetB 	= 0x67
IoffsetB 	= 0x68
UgainC 	= 0x69
IgainC 	= 0x6A
UoffsetC 	= 0x6B
IoffsetC 	= 0x6C
IgainN 	= 0x6D
IoffsetN 	= 0x6E
CS3  	= 0x6F

#	Energy Register 
APenergyT 	= 0x80
APenergyA 	= 0x81
APenergyB 	= 0x82
APenergyC 	= 0x83
ANenergyT 	= 0x84
ANenergyA 	= 0x85
ANenergyB 	= 0x86
ANenergyC 	= 0x87
RPenergyT 	= 0x88
RPenergyA 	= 0x89
RPenergyB 	= 0x8A
RPenergyC 	= 0x8B
RNenergyT 	= 0x8C
RNenergyA 	= 0x8D
RNenergyB 	= 0x8E
RNenergyC 	= 0x8F
SAenergyT 	= 0x90
SenergyA 	= 0x91
SenergyB 	= 0x92
SenergyC 	= 0x93
SVenergyT 	= 0x94
EnStatus0 	= 0x95
EnStatus1 	= 0x96
SVmeanT 	= 0x98
SVmeanTLSB 	= 0x99

#	Fundamental / Harmonic Energy Register 
APenergyTF 	= 0xA0
APenergyAF 	= 0xA1
APenergyBF 	= 0xA2
APenergyCF 	= 0xA3
ANenergyTF 	= 0xA4
ANenergyAF 	= 0xA5
ANenergyBF 	= 0xA6
ANenergyCF 	= 0xA7
APenergyTH 	= 0xA8
APenergyAH 	= 0xA9
APenergyBH 	= 0xAA
APenergyCH 	= 0xAB
ANenergyTH 	= 0xAC
ANenergyAH 	= 0xAD
ANenergyBH 	= 0xAE
ANenergyCH 	= 0xAF

#	Power and Power Factor Registers 
PmeanT 	= 0xB0
PmeanA 	= 0xB1
PmeanB 	= 0xB2
PmeanC 	= 0xB3
QmeanT 	= 0xB4
QmeanA 	= 0xB5
QmeanB 	= 0xB6
QmeanC 	= 0xB7
SAmeanT 	= 0xB8
SmeanA 	= 0xB9
SmeanB 	= 0xBA
SmeanC 	= 0xBB
PFmeanT 	= 0xBC
PFmeanA 	= 0xBD
PFmeanB 	= 0xBE
PFmeanC 	= 0xBF
PmeanTLSB 	= 0xC0
PmeanALSB 	= 0xC1
PmeanBLSB 	= 0xC2
PmeanCLSB 	= 0xC3
QmeanTLSB 	= 0xC4
QmeanALSB 	= 0xC5
QmeanBLSB 	= 0xC6
QmeanCLSB 	= 0xC7
SAmeanTLSB 	= 0xC8
SmeanALSB 	= 0xC9
SmeanBLSB 	= 0xCA
SmeanCLSB 	= 0xCB

#	Fundamental/ Harmonic Power and Voltage / Current RMS Registers 
PmeanTF 	= 0xD0
PmeanAF 	= 0xD1
PmeanBF 	= 0xD2
PmeanCF 	= 0xD3
PmeanTH 	= 0xD4
PmeanAH 	= 0xD5
PmeanBH 	= 0xD6
PmeanCH 	= 0xD7
IrmsN1 	= 0xD8
UrmsA  	= 0xD9
UrmsB  	= 0xDA
UrmsC  	= 0xDB
IrmsN0 	= 0xDC
IrmsA  	= 0xDD
IrmsB  	= 0xDE
IrmsC  	= 0xDF
PmeanTFLSB 	= 0xE0
PmeanAFLSB 	= 0xE1
PmeanBFLSB 	= 0xE2
PmeanCFLSB 	= 0xE3
PmeanTHLSB 	= 0xE4
PmeanAHLSB 	= 0xE5
PmeanBHLSB 	= 0xE6
PmeanCHLSB 	= 0xE7
UrmsALSB 	= 0xE9
UrmsBLSB 	= 0xEA
UrmsCLSB 	= 0xEB
IrmsALSB 	= 0xED
IrmsBLSB 	= 0xEE
IrmsCLSB 	= 0xEF

#	THD +N, Frequency, Angle and Temperature Regi sters 
THDNUA 	= 0xF1
THDNUB 	= 0xF2
THDNUC 	= 0xF3
THDNIA 	= 0xF5
THDNIB 	= 0xF6
THDNIC 	= 0xF7
Freq	= 0xF8
PAngleA 	= 0xF9
PAngleB 	= 0xFA
PAngleC 	= 0xFB
Temp 	= 0xFC
UangleA 	= 0xFD
UangleB 	= 0xFE
UangleC 	= 0xFF

HarmRatiosIA    = range(0x100, 0x11F)
HarmTHDRatioIA  = 0x11F
HarmRatiosIB    = range(0x120, 0x13F)
HarmTHDRatioIB  = 0x13F
HarmRatiosIC    = range(0x140, 0x15F)
HarmTHDRatioIC  = 0x15F

HarmRatiosVA    = range(0x160, 0x17F)
HarmTHDRatioVA  = 0x17F
HarmRatiosVB    = range(0x180, 0x19F)
HarmTHDRatioVB  = 0x19F
HarmRatiosVC    = range(0x1A0, 0x1BF)
HarmTHDRatioVC  = 0x1BF

FundCompValIA   = 0x1C0
FundCompValVA   = 0x1C1
FundCompValIB   = 0x1C2
FundCompValVB   = 0x1C3
FundCompValIC   = 0x1C4
FundCompValVC   = 0x1C5

DFTConfig   = 0x1D0
DFTCtrl     = 0x1D1

TempSensorConfig1   = 0x2FD
TempSensorConfig2   = 0x216
TempSensorConfig3   = 0x219

