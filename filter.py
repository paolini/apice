out = b''
with open("output1.out","rb") as f:
    data = f.read()
    for line in data.split('\n2017-07-13 '):
        date = line[:17]
        line = line[17:]
        x = line[:line.find(' [\'0x')]
        if len(x) == 80:
            print date, len(x)
            out += x
with open("output1.bin","wb") as out:
    out.write(x)
