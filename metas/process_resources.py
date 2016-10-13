from __future__ import print_function
import json
import sys

sites = ['rennes', 'grenoble', 'strasbourg', 'euratech']

if __name__ == '__main__':
    filename = 'resources.json'
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    with open(filename, 'r') as file:
        json_data = file.read()
    data = json.loads(json_data)

    for site in sites:
        motes = [mote for mote in data['items'] if mote['site'] == site and mote['uid'] != 'unknown' and mote['archi'].startswith('wsn430')]
        with open('{0}.csv'.format(site), 'w') as file:
            print('mac,x,y,z', file=file)
            for mote in motes:
                mac = '14-15-92-00-12-91-{0}-{1}'.format(mote['uid'][0:2], mote['uid'][2:4])
                x = mote['x']
                y = mote['y']
                z = mote['z']
                print('{0},{1},{2},{3}'.format(mac, x, y, z), file=file)