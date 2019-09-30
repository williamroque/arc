import shutil
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

shutil.copy('{}/.logo.png'.format(current_dir), os.path.expanduser('~/Library/Application Support/Arc/Script/logos-logo.png'))
