import os
import shutil
import zipfile

patch_path = os.path.abspath('./Patch')
if os.path.isdir(patch_path):
    if not os.path.isfile('./Patch/Patch.zip'):
        # Step.1 : Zip File Create
        targetzip = zipfile.ZipFile('./Patch/Patch.zip', 'w')
        for p, d, f in os.walk('./Patch'):
            for file in f:
                if not file == 'Patch.zip':
                    target = os.path.join(p, file)
                    relpath = os.path.relpath(target, './Patch')
                    print('Compressing ' + os.path.basename(target) + ' >>> ' + relpath)
                    targetzip.write(target, relpath, compress_type=zipfile.ZIP_DEFLATED)
        targetzip.close()
        print('Zip Done')
        # Step.2 : Copy Version Info
        version_info_file_path = os.path.abspath('./Patch/Resource/version_info.json')
        if os.path.isfile(version_info_file_path):
            shutil.copyfile(version_info_file_path, './Patch/version_info.json')
        # Step.3 : remove existing files
        for elem in os.listdir('./Patch'):
            abspath = os.path.join('./Patch', elem)
            if os.path.isdir(abspath):
                shutil.rmtree(abspath, ignore_errors=True)
    else:
        print('Zip file is alread exist!')
else:
    print('Not found patch directory!!')
