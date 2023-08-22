import serial

COM_PortName = '/dev/ttyUSB1'

#Opening the serial port

COM_Port = serial.Serial(COM_PortName, timeout=5) # open the COM port
print '\n   ',COM_PortName,'Opened' 

COM_Port.baudrate = 9600               # set Baud rate 
COM_Port.bytesize = 8                  # Number of data bits = 8
COM_Port.parity   = 'N'                # No parity
COM_Port.stopbits = 1                  # Number of Stop bits = 1

print '\n    Baud rate = ',COM_Port.baudrate
print '    Data bits = ',COM_Port.bytesize
print '    Parity    = ',COM_Port.parity
print '    Stop bits = ',COM_Port.stopbits

def send(data):
    #Controlling DTR and RTS pins to put USB2SERIAL in transmit mode

    COM_Port.setDTR(0) #DTR=0,~DTR=1 so DE = 1,Transmit mode enabled
    COM_Port.setRTS(0) #RTS=0,~RTS=1 (In FT232 RTS and DTR pins are inverted)

    print '    DTR = 0,~DTR = 1 so DE = 1,Transmit mode enabled'
    print '    RTS = 0,~RTS = 1'
    print "    sending data [{}] {}".format(''.join(x for x in data if ord(x)>=32), map(hex,map(ord,data)))
    count = COM_Port.write(data)            # Write data to serial port
    
    print '    ', count ,' bytes written'
    print '    {} written to {}'.format(data,COM_PortName)
    return count

def receive(terminator='\r', max=100):
    COM_Port.setRTS(1) #RTS=1,~RTS=0 so ~RE=0,Receive mode enabled for MAX485
    COM_Port.setDTR(1) #DTR=1,~DTR=0 so  DE=0,(In FT232 RTS and DTR pins are inverted)
    #~RE and DE LED's on USB2SERIAL board will be off
    
    print '\n    DTR = 1,~DTR = 0 so  DE = 0'
    print '    RTS = 1,~RTS = 0 so ~RE = 0,Receive mode enabled for MAX485'
    
    print '\n    Waiting for data.....\n'

    if terminator is not None:
        data = b''
        while True:
            x = COM_Port.read()
            if not x:
                ## timeout
                return None
            data += x
            if x == '\r':
                print "data read: {}".format(map(ord,data))
                return data 
    else:
        return COM_Port.read(len)

def checksum(s):
    return sum(map(ord, list(s)))
    
def write(id, *args):
    msg = 'L{:03}:{},'.format(id, ','.join(map(bytes, args)))
    prefix = chr(0xff)*6
    chk = checksum(msg)
    data = b'{}{}{:04}\r'.format(prefix, msg, chk)
    return send(data)
    
def read():
    data = receive()
    if data is None:
        return None
    while data and ord(data[0]) in [0, 0xff]:
        data = data[1:]
    if data[-1] == '\r':
        data = data[:-1]
    chk = int(data[-4:])
    data = data[:-4]
    if chk != checksum(data):
        raise RuntimeError('invalid checksum')
    print ">>{}<<".format(data)
    assert data[0] == 'R'
    assert data[-1] == ','
    id = int(data[1:4])
    if data[4] == ':':
        data = data[5:-1]
    else:
        data = data[4:-1]
    return [id] + data.split(',')
    
while True:
    try:
        line = raw_input("> ")
    except EOFError:
        print "\nquit"
        break

    args = line.split()
    cmd, args = args[0], args[1:]
        
    if cmd == "quit":
        break

    elif cmd == "receive":
        x = receive()
        print 'Data: {}\n'.format(x)

    elif cmd == "send":
        data = ' '.join(args)
        send(data)

    elif cmd == "poll":
        id, = map(int, args)
        # data = bytearray([0xff]*6)
        # data += b'L{:03}:I,0400\r'.format(id)
        # send(data)
        write(id, 'I')
        ans = read()
        print 'Response: {}\n'.format(ans)
    elif cmd == "ack":
        id, = map(int, args)
        write(id, 'U')
        ans = read()
        print 'Response: {}\n'.format(ans)
    elif cmd == "cmd":
        id, args = int(args[0]), args[1:]
        write(id, *args)
        ans = read()
        print 'Response: {}\n'.format(ans)
    else:
        print 'invalid command'
        
COM_Port.close()                       # Close the Serial port

