import os
import re

output  = []
output += ['site']

for filename in os.listdir('.'):
    
    m = re.search('([a-z]+)\.csv',filename)
    if not m:
        continue
    
    _site     = m.group(1)
    
    output += [_site]

output = '\n'.join(output)

print output

with open('sites.csv','w') as f:
    f.write(output)

raw_input("Script ended successfully. Press Enter to close.")
