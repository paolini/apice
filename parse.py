filename = "output.bin"

data=open(filename, "rb").read()
for line in data.split(chr(0x0d)):
    line = line.replace(chr(0xff),'#')
    print line

    
