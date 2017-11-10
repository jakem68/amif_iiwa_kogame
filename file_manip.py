import os

tempfile = "/home/jan/Downloads/testfile.txt"
askfile = "/home/jan/Downloads/remote.ask"
line1 = '1\n'
line2 = '2\n'
line3 = '3\n'
line4 = '4\n'
line5 = '5\n'
line6 = '6\n'
line7 = '7\n'

try:
    with open(tempfile, 'w') as f:
        f.writelines([line1, line2, line3, line4, line5, line6, line7])
except:
    print('could not create tempfile')
    pass

try:
    os.rename(tempfile, askfile)
except:
    print('could not rename tempfile to askfile')
    pass

with open(askfile, 'r') as f_ask:
    print f_ask.read()

os.remove(askfile)

ask_file_exists = os.path.isfile(askfile)
print(ask_file_exists)