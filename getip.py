#import socket
#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#    try:
#        s.connect(("10.255.255.255", 1))
#        print(s.getsockname()[0])
#    except:
#        print("127.0.0.1")
#    finally:  s.close()

import socket
def get_ip():
    ip = '127.0.0.1'
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            pass
        finally:
            s.close()
    return ip

print(get_ip())

#   alias getip='python3 -c "import socket
#   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#   try:
#       s.connect((\"10.255.255.255\", 1))
#       print(s.getsockname()[0])
#   except:
#       print(\"127.0.0.1\")
#   finally:  s.close()"
#   '
