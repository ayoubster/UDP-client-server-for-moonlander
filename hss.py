import socket
import struct
import datetime

UDP_IP = "127.0.0.1" # local computer
UDP_PORT = 12778 # Port to connect to ./simulator 

sock = socket.socket(socket.AF_INET, # IPv4 
                      socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) # Binding to port

def convert(sensorvalues):
# Convert UINT_16 values ranging from 0-65535 to meters 
    conversion = list(sensorvalues)
    conversion[0] = (int(conversion[0]) / 65.535) * 100
    conversion[1] = (int(conversion[1]) / 65.535) * 100
    conversion[2] = (int(conversion[2]) / 65.535) * 100
    return conversion

while True:
    data, addr = sock.recvfrom(8192) # buffer size is 8192 bytes
    # Look for the LASER_ALTIMETER type corresponding to 0xaa01
    if not data.startswith(b'\xaa\x01') and len(data) != 12: 
        continue
    else:
        num_values = (len(data) - 6) // 2 # Sensor values are last 6 bytes
        timevalues = (len(data) - 10) // 2 # Time values are bytes 3-6
        values = struct.unpack('>' + 'H' * num_values, data[6:]) # Big Endian
        time = struct.unpack('>' + 'I' * timevalues, data[2:6]) 
        print("Bytes received: %s" % len(data))
        print("Received message: %s" % data)
        print("Mission time elapsed: %s (hh/mm/ss)" % str(datetime.timedelta(seconds = float(time[0]//1e3))))
        print("Sensor Readings: %s cm\n" % convert(values))
        
	# Check when sensor value is less than or equal to 40cm, send packet to cut off other subsystems
        if convert(values)[0] <= 40 and convert(values)[1] <= 40 and convert(values)[2] <= 40:
            print("Sensors height is less than 40cm, sending ENGINE_CUTOFF packet to all other subsytems")
            print("Shutting down...")
            msg = b'\xaa\x11'
            sock.sendto(msg, (UDP_IP, UDP_PORT))
            sock.close()
            break
