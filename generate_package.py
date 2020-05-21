import sys
import os

import re

import json

framework_path = './src/framework'

package_path = input('Package path> ')
output_path = input('Output path> ')

if package_path and output_path:
    output = {"scripts": []}

    framework_scripts = list(
        map(
            lambda x: '{}/{}'.format(framework_path, x),
            os.listdir(framework_path)
        )
    )
    package_scripts = list(
        map(
            lambda x: '{}/{}'.format(package_path, x),
            os.listdir(package_path)
        )
    )

    with open('{}/{}'.format(package_path, 'manifest.json'), 'r') as f:
        output['manifest'] = json.loads(f.read())

    for script_path in filter(lambda x: re.match(r'^.+\.py$', x), framework_scripts + package_scripts):
        with open(script_path, 'r') as f:
            output["scripts"].append({
                "path": re.search(r'(?<=/)\w+\.py$', script_path).group(0),
                "contents": f.read()
            })

    with open('logos-logo.png', 'rb') as f:
        raw_image = f.read().decode('latin1')

    with open(output_path, 'w', encoding='latin1') as f:
        f.write(raw_image + '|===|' + json.dumps(output))
