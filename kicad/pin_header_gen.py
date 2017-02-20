#!/usr/bin/python
''' Read in netlist and generate header file with pin/port definitions
    for the selected component (by reference designator) 

    Example usage:
    pin_header_gen.py --filename project.net --refdes U3 > pins.h
'''

import argparse
import sys
import re
from kicadnetlistreader import KiCadNetlistReader

port_re = re.compile('P([A-Z])([0-9]{1,2})')

parser = argparse.ArgumentParser()
parser.add_argument('--filename', help="netlist filename", required=True)
parser.add_argument('--refdes', help="Reference designator for part", required=True)
args = parser.parse_args()

reader = KiCadNetlistReader(args.filename)

c_pins = reader.components[args.refdes]['pins']
p_pins = reader.parts[reader.components[args.refdes]['part']]['pins']

print('#ifndef __PINS_H__')
print('#define __PINS_H__\n')

for pin in sorted(p_pins.keys(), key=lambda x: int(x)):
    part_pin_name = p_pins.get(pin)
    component_pin_name = c_pins.get(pin)

    if ('"Net-(' + args.refdes) in component_pin_name:
        continue

    m = port_re.match(part_pin_name)
    if m:
        port = m.group(1)
        pin = m.group(2)

        print('#define _' + component_pin_name + '_PORT GPIO' + port)
        print('#define _' + component_pin_name + '_PIN ' + pin)
        print('')

print('#endif // __PINS_H__\n')
