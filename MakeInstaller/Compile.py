import os
import shutil
import py_compile

curpath = os.path.dirname(os.path.abspath(__file__))
projpath = os.path.dirname(curpath)
paths = [
    os.path.join(projpath, "Include"),
    os.path.join(projpath, "Include/Task"),
    os.path.join(projpath, "Include/Util"),
    os.path.join(projpath, "Include/Widget"),
]

APP_CLASSNAME = "MACRO"
default_install_path = r'C:\MACRO\{}'.format(APP_CLASSNAME)
include_path = os.path.join(default_install_path, 'Include')

export_path = os.path.join(curpath, "Compile")
shutil.rmtree(path=export_path, ignore_errors=True)
if not os.path.isdir(export_path):
    os.mkdir(export_path)

for path in paths:
    p = os.path.abspath(path)
    # 해당 경로 내 모든 .py 파일을 컴파일한다
    for k, _, files in os.walk(p):
        for filename in files:
            name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[-1]
            if ext == '.py' and k == os.path.abspath(path):
                pyPath = os.path.join(k, filename)
                resPath = os.path.abspath(export_path + path.replace(projpath, '/'))
                print('>> Try to compile "' + pyPath + '"')
                try:
                    exp = resPath + '\\' + name + '.pyc'
                    print(exp)
                    res = py_compile.compile(
                        file=pyPath,
                        cfile=os.path.abspath(exp),
                        dfile=os.path.join(include_path, filename),
                        optimize=-1,
                        doraise=True
                    )
                    print('Success! : ' + res)
                except py_compile.PyCompileError as e:
                    print('Failed! : ' + str(e))
