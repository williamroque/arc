import sys
import os

import json

script_path = input('Script path> ')
output_path = input('Output path> ')

output = {}

if script_path:
    with open(script_path, 'r') as f:
        output['script'] = f.read()

with open(output_path + '.apf', 'w') as f:
    f.write(json.dumps(output))
