import os


def ensure_path_exist(path: str):
    targetpath = os.path.abspath(path)
    if not os.path.isdir(targetpath):
        if os.name == 'nt':
            pathsplit = targetpath.split('\\')
            ptemp = str(pathsplit[0]) + '\\'
        else:
            pathsplit = targetpath.split('/')
            ptemp = str(pathsplit[0]) + '/'
        for i in range(len(pathsplit) - 1):
            p = pathsplit[i + 1]
            ptemp = os.path.join(ptemp, p)
            ptemp = os.path.abspath(ptemp)
            if not os.path.isdir(ptemp):
                os.mkdir(ptemp)
