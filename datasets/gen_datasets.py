import os
import re

output  = []
output += ['site,timestamp,filename']

for filename in os.listdir('.'):
    
    print filename
    
    m = re.search('([a-z]+)\-([\.0-9]+)\-([\.0-9]+)\.csv',filename)
    if not m:
        continue
    
    _site     = m.group(1)
    _date     = m.group(2)
    _time     = m.group(3)
    
    output += [
        '{0},{1}-{2},{3}'.format(
            _site,
            _date,_time,
            filename
        )
    ]

output = '\n'.join(output)

print output

with open('datasets.csv','w') as f:
    f.write(output)

raw_input("Script ended successfully. Press Enter to close.")
