import os

curpath = os.path.dirname(__file__)

for (p, d, files) in os.walk(curpath):
    for file in files:
        if 'MACRO Setup' in file and os.path.splitext(file)[-1] == '.exe':
            delpath = os.path.join(p, file)
            print('Removing %s' % delpath)
            os.remove(delpath)
