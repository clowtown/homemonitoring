#!/usr/bin/python3

# Import MCP3008 library.
import Adafruit_MCP3008
import requests

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
values = [0]*8
for i in range(8):
    # The read_adc function will get the value of the specified channel (0-7).
    values[i] = mcp.read_adc(i)
r = requests.get("http://10.0.1.21:80/tempOhms/{}".format(values[0]))

