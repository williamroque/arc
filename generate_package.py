import sys
import os

import re

import json

script_path = './src'
output_path = input('Output path> ')

if script_path and output_path:
    output = {}

    for file in filter(lambda x: re.match(r'^.+\.py$', x), os.listdir(script_path)):
        with open('{}/{}'.format(script_path, file), 'r') as f:
            output[file] = f.read()

    with open('logos-logo-png', 'rb') as f:
        output['logo'] = str(f.read())

    with open('arc_v{}.apf'.format(output_path), 'w') as f:
        f.write(json.dumps(output))
