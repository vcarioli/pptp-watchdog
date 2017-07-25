#!/usr/bin/env /usr/bin/python3
import sys

def	test():
	try:
		print('Enter try')
		a = 3 / 0
		return
	except:
		pass
	finally:
		print('exiting try')



if __name__ == "__main__":
	print('Enter main')

	test()

	print('Exit main')
	print(sys.argv[1:])

