import time
try:
	while True:
		print('in esecuzione')
		time.sleep(1.5)
except KeyboardInterrupt:
	pass
finally:
	print('FINE')
		