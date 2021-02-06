import sys
import subprocess

package_array =  [
   "PyQt5"
   ]
def install_all():
   for package in package_array:
      subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
install_all()