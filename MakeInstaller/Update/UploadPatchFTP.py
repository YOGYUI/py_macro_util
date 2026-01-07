import os
import json
import ftplib
import zipfile

APP_NAME = 'MACRO'
CUR_PATH = os.path.dirname(os.path.abspath(__file__))


def connectToFTPServer(host, port, user, passwd, timeout):
    try:
        ftp = ftplib.FTP()
        ftp.connect(host=host, port=port, timeout=timeout)
        ftp.login(user=user, passwd=passwd)
        return ftp
    except Exception as e:
        return str(e)


def uploadFilesToFTPServer(ftp, pathList, app_version):
    try:
        for elem in pathList:
            p = elem['path']
            if p != '':
                dirss = p.split('\\')
                curdir = app_version
                dircnt = len(dirss)
                for d in dirss:
                    curftplst = ftp.nlst()
                    curdir += '\\'+d
                    if d not in curftplst:
                        ftp.mkd(d)
                        print('[FTP Make Directory] %s' % curdir)
                    ftp.cwd(d)
            else:
                dircnt = 0
            all_files = elem['files']
            ppath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Patch'))
            for filename in all_files:
                filepath = os.path.join(os.path.join(ppath, p), filename)
                ftp.storbinary('STOR ' + filename, open(filepath, 'rb'))
                print('[FTP File Upload] %s\\%s\\%s' % (str_app_version, path, filename))
            ftp.cwd('../'*dircnt)
    except Exception as e:
        print('uploadFilesToFTPServer::' + str(e))


if __name__ == "__main__":
    ftp_info_path = os.path.abspath("./ftp_info.json")
    if os.path.isfile(ftp_info_path):
        with open(ftp_info_path, "r") as fp:
            ftp_info = json.load(fp)

        for info in ftp_info:
            ftp_host = info.get("host")
            ftp_port = info.get("port")
            ftp_path = info.get("path")
            ftp_id = info.get("id")
            ftp_password = info.get("password")
            ftp_ = connectToFTPServer(host=ftp_host, port=ftp_port, user=ftp_id, passwd=ftp_password, timeout=30)
            print('FTP >> ' + ftp_host + ':%d' % ftp_port)
            ftp_.cwd(ftp_path)
            if APP_NAME not in ftp_.nlst():
                ftp_.mkd(APP_NAME)
            ftp_.cwd(APP_NAME)
            patch_path = os.path.join(CUR_PATH, 'Patch')
            if os.path.isdir(patch_path):
                if 'Patch.zip' in os.listdir(patch_path):
                    print("Zip File Patch Found")
                    verPath = os.path.join(patch_path, 'version_info.json')
                    zipPath = os.path.join(patch_path, 'Patch.zip')
                    with open(verPath, "r") as fp2:
                        ver_info = json.load(fp2)
                    zf = zipfile.ZipFile(zipPath)
                    if isinstance(zf, str):
                        print('[Error] Zip File Error...(%s)' % zf)
                    else:
                        str_app_version = ver_info.get("version", "0.0.0")
                        fileCnt = len(zf.filelist)
                        zf.close()
                        ver_info["files"] = '{:d}'.format(fileCnt)
                        with open(verPath, "w") as fp3:
                            json.dump(ver_info, fp3)
                        # 버전명 폴더를 생성한다 (FTP)
                        if str_app_version not in ftp_.nlst():
                            ftp_.mkd(str_app_version)
                            print('[FTP Make Directory] %s' % str_app_version)
                        ftp_.cwd(str_app_version)
                        # 업로드할 파일 경로 리스트를 생성한다
                        _pathList = list()
                        for (path, dirs, files) in os.walk(patch_path):
                            if len(files) > 0:
                                _pathList.append({'path': os.path.abspath(path)[len(patch_path):], 'files': files})
                        # 업로드 함수 호출
                        uploadFilesToFTPServer(ftp_, _pathList, str_app_version)
            else:
                print('[Error] Not Found Patch Folder...')
            ftp_.close()
