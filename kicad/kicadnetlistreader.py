''' Class to read in kicad netlist into python dictionaries '''
import re

comp_re = re.compile('\(comp \(ref ([A-Z]+[0-9]+)\)')
comp_val_re = re.compile('\(value (.+)\)')
comp_foot_re = re.compile('\(footprint (.+)\)')
comp_part_re = re.compile('\(libsource \(lib (.+)\) \(part (.+)\)\)')

part_re = re.compile('\(libpart \(lib (.+)\) \(part (.+)\)')
part_pin_re = re.compile('\(pin \(num ([0-9A-Z-a-z]+)\) \(name (.+)\) \(type ([A-Za-z0-9_-]+)\)\)')

net_re = re.compile('\(net \(code ([0-9])+\) \(name \/?(.+)\)')
net_node_re = re.compile('\(node \(ref ([A-Za-z]+[0-9]+)\) \(pin ([0-9]+)\)\)')

class KiCadNetlistReader(object):
    def __init__(self, filename):
        self.mode = None

        self.modeproc = {
            'components': self.component_fn,
            'libparts': self.part_fn,
            'nets': self.netlist_fn,
        }

        self.components = {}
        self.nets = {}
        self.parts = {}

        with open(filename) as file:
            reading = True
            while reading:
                line = file.readline()
                if line == '':
                    break

                self.processLine(line.strip())

            # Relate pins on component to net names
            self.updateComponents()

    def component_fn(self, line):
        # Component regex match
        m = comp_re.match(line)
        if m:
            refdes = m.group(1)
            if refdes not in self.components:
                self.components[refdes]={'pins':{}}
                self.current_refdes = refdes
            return

        # Value regex match
        m = comp_val_re.match(line)
        if m:
            refdes = self.current_refdes
            if refdes in self.components:
                self.components[refdes]['value'] = m.group(1)

        # Footprint regex match
        m = comp_foot_re.match(line)
        if m:
            refdes = self.current_refdes
            if refdes in self.components:
                self.components[refdes]['footprint'] = m.group(1)

        # Part regex match
        m = comp_part_re.match(line)
        if m:
            refdes = self.current_refdes
            if refdes in self.components:
                self.components[refdes]['lib'] = m.group(1)
                self.components[refdes]['part'] = m.group(2)

    def part_fn(self, line):
        # Part regex match
        m = part_re.match(line)
        if m:
            name = m.group(2)
            if name not in self.parts:
                self.parts[name] = {'pins':{}, 'lib':m.group(1)}
                self.current_part_name = name
            return

        # pin regex match
        m = part_pin_re.match(line)
        if m:
            part_name = self.current_part_name
            if part_name in self.parts:
                self.parts[part_name]['pins'][m.group(1)] = m.group(2)

    def netlist_fn(self, line):
        # Netlist regex match
        m = net_re.match(line)
        if m:
            code = m.group(1)
            name = m.group(2)

            if name not in self.nets:
                self.nets[name]={'code':code, 'nodes':{}}
                self.current_net_name = name
            return

        # Node regex match
        m = net_node_re.match(line)
        if m:
            net = self.current_net_name
            if net in self.nets:
                refdes = m.group(1)
                if refdes not in self.nets[net]['nodes']:
                    self.nets[net]['nodes'][refdes] = []
                self.nets[net]['nodes'][refdes].append(m.group(2))

    def updateComponents(self):
        for net in self.nets:
            for node in self.nets[net]['nodes']:
                if self.components[node]:
                    for pin in self.nets[net]['nodes'][node]:
                        self.components[node]['pins'][pin] = net

    def processLine(self, line):
        if line == '(components':
            self.mode = 'components'
            return
        elif line == '(libparts':
            self.mode = 'libparts'
            return
        elif line == '(libraries':
            self.mode = None
        elif line == '(nets':
            self.mode = 'nets'

        if self.mode in self.modeproc:
            self.modeproc[self.mode](line)
