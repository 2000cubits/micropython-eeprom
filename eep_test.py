# eep_test.py MicroPython driver for Microchip EEPROM devices.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2019 Peter Hinch

import uos
from machine import I2C, Pin
from eeprom import EEPROM, T24C512

# Return an EEPROM array. Adapt for platforms other than Pyboard or chips
# smaller than 64KiB.
def get_eep():
    if uos.uname().machine.split(' ')[0][:4] == 'PYBD':
        Pin.board.EN_3V3.value(1)
    eep = EEPROM(I2C(2), T24C512)
    print('Instantiated EEPROM')
    return eep

# Dumb file copy utility to help with managing EEPROM contents at the REPL.
def cp(source, dest):
    if dest.endswith('/'):  # minimal way to allow
        dest = ''.join((dest, source.split('/')[-1]))  # cp /sd/file /eeprom/
    with open(source, 'rb') as infile:  # Caller should handle any OSError
        with open(dest,'wb') as outfile:  # e.g file not found
            while True:
                buf = infile.read(100)
                outfile.write(buf)
                if len(buf) < 100:
                    break

def test():
    eep = get_eep()
    sa = 1000
    for v in range(256):
        eep[sa + v] = v
    for v in range(256):
        if eep[sa + v] != v:
            print('Fail at address {} data {} should be {}'.format(sa + v, eep[sa + v], v))
            break
    else:
        print('Test of byte addressing passed')
    data = uos.urandom(30)
    sa = 2000
    eep[sa:sa + 30] = data
    if eep[sa:sa + 30] == data:
        print('Test of slice readback passed')

def fstest(format=False):
    eep = get_eep()
    if format:
        uos.VfsFat.mkfs(eep)
    vfs=uos.VfsFat(eep)
    try:
        uos.mount(vfs,'/eeprom')
    except OSError:  # Already mounted
        pass
    print('Contents of "/": {}'.format(uos.listdir('/')))
    print('Contents of "/eeprom": {}'.format(uos.listdir('/eeprom')))
    print(uos.statvfs('/eeprom'))

def full_test():
    eep = get_eep()
    page = 0
    for sa in range(0, len(eep), 128):
        data = uos.urandom(128)
        eep[sa:sa + 128] = data
        if eep[sa:sa + 128] == data:
            print('Page {} passed'.format(page))
        else:
            print('Page {} readback failed.'.format(page))
        page += 1