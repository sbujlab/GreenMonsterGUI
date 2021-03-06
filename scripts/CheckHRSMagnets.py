import os
import time
import subprocess
import socket
from argparse import ArgumentParser
from datetime import datetime
from decimal import Decimal

parser = ArgumentParser()
parser.add_argument("arg", nargs='?', type=str, help="Input Flag", default="NULL")
args = vars(parser.parse_args())

Magnet_set_epics = ["MQ171L.S","TSDAC18_L0_setDAC","HacL_D1_DYNPWR:ISET","TSDAC18_L1_setDAC","MQ172R.S","TSDAC18_R0_setDAC","HacR_P0set","TSDAC18_R1_setDAC","hesDipole:setAmps","MSUPERBIGBITE.S"]
Magnet_set_points = [225.387,934.273,744.0,981.301,230.916,925.955,2.1835,981.301,801.248,-801.248]
Magnet_readback_epics = ["MQ171LM","HacL_Q2_HP3458A:IOUT","HacL_D1_HP3458A:IOUT","HacL_Q3_HP3458A:IOUT","MQ172RM","HacR_Q2_HP3458A:IOUT","HacR_D1_HP3458A:IOUT","HacR_Q3_HP3458A:IOUT","hesDipole:current","MSUPERBIGBITEreadcalc"]
Magnet_readback_points = [225.504,931.736,741.172,980.769,230.893,924.77,762.517,977.753,802.586,-799.336]
Magnet_readback_tolerances = [0.20,0.10,0.05,0.05,0.10,0.1,0.05,0.1,0.1,0.1]

AllGood = True
i = 0
nTrip = 0
while i < len(Magnet_set_epics):
  #cmds = ['caget', '-t', '-w 1', 'IGL0I00C1068_DAC06']
  cmds = ['caget', '-t', '-w 1', str(Magnet_set_epics[i])]
  cond_out = "NULL"
  cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip().decode('ascii') # Needs to be decoded... be careful 
  if "Invalid" in cond_out:
    #print("Error, {} not found".format(Magnet_set_epics[i]))
    i = i+1
    continue
  if Magnet_set_points[i]!=float(cond_out):
    nTrip = nTrip+1
    AllGood = False
    if nTrip < 2:
      print("ERROR: Magnet set point {} = {}\n  Not equal to correct value of {}".format(Magnet_set_epics[i],cond_out,Magnet_set_points[i]))

  cmds = ['caget', '-t', '-w 1', str(Magnet_readback_epics[i])]
  cond_out = "NULL"
  cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip().decode('ascii') # Needs to be decoded... be careful 
  if "Invalid" in cond_out:
    #print("Error, {} not found".format(Magnet_readback_epics[i]))
    i = i+1
    continue
  if 100.0*abs(Magnet_readback_points[i]-float(cond_out))/(Magnet_readback_points[i]) > Magnet_readback_tolerances[i]:
    nTrip = nTrip+1
    if nTrip < 2:
      print("ERROR: Magnet readback point \n{} = {}\n  This is more than {} % away\n  Correct value is {}\n  It is {} % away".format(Magnet_readback_epics[i],cond_out,Magnet_readback_tolerances[i],Magnet_readback_points[i], 100*(Magnet_readback_points[i]-float(cond_out))/Magnet_readback_points[i]))
    AllGood = False
  i = i+1

if AllGood is False:
  if nTrip >= 2:
    print("MAJOR ERROR: multiple problems\n  Check GUIs and stripcharts")
  print("Please check the magnet set \npoints and readbacks. If a \nDipole is bad then check \ndetector alignment\n")
else:
  print("OK")
