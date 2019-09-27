import sys
import os

import json
import re

script_path = input('Script path> ')
form_dir = input('Form dir> ')
output_path = input('Output path> ')

output = {}

is_json = re.compile('\.json$')

if script_path:
    with open(script_path, 'r') as f:
        output['script'] = f.read()
if form_dir:
    output['forms'] = []
    for path in os.listdir(form_dir):
        if is_json.search(path):
            with open(form_dir + '/' + path, 'r') as f:
                output['forms'].append(json.loads(f.read()))

with open(output_path + '.apf', 'w') as f:
    f.write(json.dumps(output))
