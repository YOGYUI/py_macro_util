import os
import configparser
from datetime import datetime


if __name__ == '__main__':
    curpath = os.path.dirname(os.path.abspath('./'))
    version_info_path = os.path.join(curpath, 'VersionInfo')
    version_info_file_path = os.path.join(version_info_path, 'version.ini')
    strAppVersion = '0.0.0.0'
    if os.path.isfile(version_info_file_path):
        config = configparser.ConfigParser()
        try:
            result = config.read(version_info_file_path, encoding='cp949')
        except Exception:
            result = config.read(version_info_file_path, encoding='utf-8')
        if len(result) > 0:
            section_basic = config['Basic']
            strAppVersion = section_basic['APP_VERSION']
    if len(strAppVersion.split('.')) == 3:
        strAppVersion += '.0'
    verval = [int(x) for x in strAppVersion.split('.')]
    strverval = ', '.join(['%d' % x for x in verval])

    file_description = 'Keyboard & Mouse Macro Utility'
    app_name = 'MACRO'
    year = datetime.now().year
    temp = '-%d' % year if year > 2026 else ''
    cpr = '(C) 2026%s, SEUNGHEE, LEE. All Rights Reserved.' % temp

    with open('./file_version_info.txt', 'w') as fp:
        fp.write("# UTF-8\n#\n")
        fp.write("# For more details about fixed file info 'ffi' see:\n")
        fp.write("# http://msdn.microsoft.com/en-us/library/ms646997.aspx\n")
        fp.write("VSVersionInfo(\n")
        fp.write("  ffi=FixedFileInfo(\n")
        fp.write("    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)\n")
        fp.write("    # Set not needed items to zero 0.\n")
        fp.write("    filevers=(%s),\n" % strverval)
        fp.write("    prodvers=(%s),\n" % strverval)
        fp.write("    # Contains a bitmask that specifies the valid bits 'flags'r\n")
        fp.write("    mask=0x3f,\n")
        fp.write("    # Contains a bitmask that specifies the Boolean attributes of the file.\n")
        fp.write("    flags=0x1,\n")
        fp.write("    # The operating system for which this file was designed.\n")
        fp.write("    # 0x4 - NT and there is no need to change it.\n")
        fp.write("    OS=0x4,\n")
        fp.write("    # The general type of file.\n")
        fp.write("    # 0x1 - the file is an application.\n")
        fp.write("    fileType=0x1,\n")
        fp.write("    # The function of the file.\n")
        fp.write("    # 0x0 - the function is not defined for this fileType\n")
        fp.write("    subtype=0x0,\n")
        fp.write("    # Creation date and time stamp.\n")
        fp.write("    date=(0, 0)\n")
        fp.write("    ),\n")

        fp.write("  kids=[\n")
        fp.write("    StringFileInfo(\n")
        fp.write("      [\n")
        fp.write("      StringTable(\n")
        fp.write("        u'040904E4',\n")
        fp.write("        [StringStruct(u'FileDescription', u'%s'),\n" % file_description)
        fp.write("        StringStruct(u'FileVersion', u'%s'),\n" % strAppVersion)
        fp.write("        StringStruct(u'InternalName', u'%s.exe'),\n" % app_name)
        fp.write("        StringStruct(u'LegalCopyright', u'%s'),\n" % cpr)
        fp.write("        StringStruct(u'OriginalFilename', u'%s.exe'),\n" % app_name)
        fp.write("        StringStruct(u'ProductName', u'%s'),\n" % app_name)
        fp.write("        StringStruct(u'ProductVersion', u'%s'),\n" % strAppVersion)
        fp.write("        StringStruct(u'Comments', u'Developer: SEUNGHEE, LEE')])\n")
        fp.write("      ]), \n")
        fp.write("    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])\n")
        fp.write("  ]\n")
        fp.write(")\n")
