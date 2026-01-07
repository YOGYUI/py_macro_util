# FTP 저장소의 모든 버전에 대한 정보를 담은 XML File을 생성
import os
import _io
import time
import ftplib
import json
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from collections import OrderedDict

APP_NAME = 'MACRO'


def connectToFTPServer(host, port, user, passwd, timeout):
    try:
        ftpconn = ftplib.FTP()
        ftpconn.connect(host=host, port=port, timeout=timeout)
        ftpconn.login(user=user, passwd=passwd)
        return ftpconn
    except Exception as e:
        return str(e)


def convertVersionString(strVersion: str):
    try:
        split = strVersion.split('.')
        if len(split) >= 2:
            version = int(split[0])
            for i in range(len(split) - 1):
                version += int(split[i + 1]) * (0.1 ** (i + len(split[i + 1])))
            return version
        else:
            return 0.0
    except ValueError:
        return 0.0
    except Exception:
        return 0.0


def makeVersionListFromFile(ftp, versionName: str, modifyDate: str, zipped: bool) -> dict:
    info_dict = {}
    try:
        if 'version_info.json' in ftp.nlst():
            ftp.retrbinary('RETR ' + 'version_info.json', open('./temp.json', 'wb').write)
            with open("./temp.json", "r") as fp_:
                info_ = json.load(fp_)
                str_app_version = info_.get("version", "0.0.0")
                file_count = info_.get("files", 0)
                required = info_.get("required", "0.0.0")
                if str_app_version == versionName:
                    info_dict['versionName'] = versionName
                    info_dict['versionValue'] = convertVersionString(versionName)
                    info_dict['modify'] = modifyDate
                    info_dict['files'] = file_count
                    # timezone align
                    localUTCOffset = time.timezone * 100 // 3600  # local utc offset, (ex) -32400 = -9H * 3600
                    if localUTCOffset >= 0:
                        tzStr = '+%04d' % abs(localUTCOffset)
                    else:
                        tzStr = '-%04d' % abs(localUTCOffset)
                    info_dict['datetime'] = datetime.strptime(modifyDate + '-' + tzStr, '%Y%m%d%H%M%S-%z')
                    info_dict['datetime'] = info_dict['datetime'].astimezone(tz=timezone.utc)
                    info_dict['zipped'] = zipped
                    info_dict['required'] = required
            os.remove('./temp.json')
    except Exception:
        pass
    return info_dict


def writeXmlFile(elem: ET.Element, path: str = '', fp: _io.TextIOWrapper = None, level: int = 0):
    if fp is None:
        _fp = open(path, 'w', encoding='utf-8')
        _fp.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + '\n')
    else:
        _fp = fp
    _fp.write('\t' * level)
    _fp.write('<' + elem.tag)
    for key in elem.keys():
        fp.write(' ' + key + '="' + str(elem.attrib[key]) + '"')
    if len(list(elem)) > 0:
        _fp.write('>\n')
        for child in list(elem):
            writeXmlFile(child, fp=_fp, level=level + 1)
        _fp.write('\t' * level)
        _fp.write('</' + elem.tag + '>\n')
    else:
        if elem.text is not None:
            txt = elem.text
            txt = txt.replace('\r', '')
            txt = txt.replace('\n', '')
            txt = txt.replace('\t', '')
            if len(txt) > 0:
                _fp.write('>' + txt + '</' + elem.tag + '>\n')
            else:
                _fp.write('/>\n')
        else:
            _fp.write('/>\n')
    if level == 0:
        _fp.close()


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
            ftp_.cwd(ftp_path)

            if APP_NAME not in ftp_.nlst():
                ftp_.mkd(APP_NAME)
            ftp_.cwd(APP_NAME)
            nlst = []
            versionList = []
            ftp_.retrlines('MLSD', nlst.append)

            for n in nlst:
                _split = n.split(';')
                _modifyDate = _split[0].split('=')[-1]  # modify=YYYYmmddHHMMSS
                _versionName = _split[-1].strip()
                typefind = list(filter(lambda x: 'type=' in x, _split))[0]
                typename = typefind.split('=')[-1]
                if typename == 'dir':
                    print('query version information from %s' % _versionName)
                    ftp_.cwd(_versionName)
                    if 'Patch.zip' in ftp_.nlst():
                        versioninfo = makeVersionListFromFile(ftp_, _versionName, _modifyDate, zipped=True)
                        versionList.append(versioninfo)
                    ftp_.cwd('../')

            xmlpath = os.path.abspath('./VersionInfo.xml')
            if os.path.isfile(xmlpath):
                os.remove(xmlpath)

            print('making version information xml file')
            root = ET.Element('VersionInfo')
            for v in versionList:
                d = OrderedDict()
                d['files'] = v['files']
                d['modify'] = v['modify']
                d['zipped'] = v['zipped']
                if v['required'] is not None:
                    d['required'] = v['required']
                node = ET.Element('Ver' + v['versionName'], d)  # 태그 이름이 숫자로만 이루어지면 안된다!
                root.append(node)
            writeXmlFile(root, xmlpath)

            # Step.3 : XML File을 FTP에 업로드한다
            if 'VersionList' not in ftp_.nlst():
                print('ftp: making folder "VersionList"')
                ftp_.mkd('VersionList')
            ftp_.cwd('VersionList')
            print('uploading version information xml file to ftp')
            ftp_.storbinary('STOR ' + os.path.basename(xmlpath), open(xmlpath, 'rb'))

            # Step.4 : XML File 제거
            print('making version information xml file')
            # os.remove(xmlpath)

            ftp_.close()
