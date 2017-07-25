import os
response = os.system('ping -c 1 -q www.google.com > /dev/null 2>&1')
if response:
	print("not found")

import subprocess

# RUNNING_VMS=($($sudo vboxmanage list runningvms | sed -e 's/"\(.*\)".*$/\1/'))
# response = subprocess.check_output('vboxmanage list vms', shell=True)
#for s in str(response, 'utf-8').split('\n'):
#	s = s.split(' ')[0].strip('"')
#	if s == 'pptp':
#		print(s)
