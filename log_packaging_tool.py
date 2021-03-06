from datetime import datetime
import json
import os
import shutil
import win_eventlog
import xml.etree.ElementTree as ET


def get_current_time():
    now = datetime.now()

    return now.strftime('%Y%m%d_(%H-%M-%S)')


def get_config():
    config_name = 'config.xml'
    backup_folder_list = []
    backup_file_list = []
    ret = True

    if not os.path.exists(config_name):
        ret = False
        print('config.xml is missing.')

    try:
        tree = ET.parse(config_name)
        root = tree.getroot()
    except:
        ret = False
        print('Open config.xml fail')

    if ret:
        for element in root.find('BackupFolderList'):
            if element.tag == 'Path':
                path = element.text

                if os.path.exists(path) and os.path.isdir(path):
                    backup_folder_list.append(path)
                else:
                    ret = False
                    print(f'Folder path "{path}" is not exist, please check the "BackupFolderList" path in the config.xml')
                    break

    if ret:
        for element in root.find('BackupFileList'):
            if element.tag == 'Path':
                path = element.text

                if os.path.exists(path) and os.path.isfile(path):
                    backup_file_list.append(path)
                else:
                    ret = False
                    print(f'File path "{path}" is not exist, please check the "BackupFileList" path in the config.xml')
                    break

    return ret, backup_folder_list, backup_file_list


def main():
    ret, backup_folder_list, backup_file_list = get_config()

    if not ret:
        return

    output_dir = os.path.join(os.getcwd(), 'output')
    temp_dir = os.path.join(output_dir, 'Log')

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.makedirs(temp_dir)
    os.makedirs(os.path.join(temp_dir, 'Folders'))
    os.makedirs(os.path.join(temp_dir, 'Files'))
    os.makedirs(os.path.join(temp_dir, 'EventLog'))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. export eventlog
    for log_type in win_eventlog.ELogType:
        if not win_eventlog.export(log_type, os.path.join(temp_dir, 'EventLog')):
            print('Log Packaging Fail !!!')
            input("Press any key to continue...")

            return False

    # 2. copy folder
    for folder_path in backup_folder_list:
        if os.path.isdir(folder_path):
            print(f'Copy folder : {folder_path}')
            shutil.copytree(folder_path, os.path.join(temp_dir, 'Folders', os.path.basename(folder_path)))
        else:
            print(f'Folder path "{folder_path}" is not exist, please check the "BackupFolderList" path in the config.xml')

            return

    # 3. copy file
    for file_path in backup_file_list:
        if os.path.isfile(file_path):
            print(f'Copy file : {file_path}')
            shutil.copyfile(file_path, os.path.join(temp_dir, 'Files', os.path.basename(file_path)))
        else:
            print(f'File path "{file_path}" is not exist, please check the "BackupFileList" path in the config.xml')

            return

    # 4. zip file
    zip_name = f'Log_{get_current_time()}'
    output_zip_name = os.path.join(output_dir, zip_name)
    shutil.make_archive(output_zip_name, format='zip', root_dir=temp_dir)
    print(f'Zip {output_zip_name} success !!!')

    # 5. remove temp dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    print('Log Packaging Finish !!!')
    input('Press any key to continue...')

    return True


if __name__ == '__main__':
    main()
