from tkinter import Tk, Label, Frame, Button, messagebox, Toplevel, Text, Entry, Checkbutton
from tkinter.ttk import Notebook, Combobox
import tkinter as tk
import subprocess
import os
import winreg
import tempfile
import pyperclip
import re
import inspect
import shutil
import io
import socket
from datetime import datetime
import time
import zipfile
from tkinter import filedialog

EncryptionKey = r'+EsQIZSAj7rT28Jx5nF+yYhjkOTTdCH6dOub1MYMfvY='

pso_path = '/sdcard/Android/data/com.kaboom.BeyondStar/files/ProgramBinaryCache'


confg_pak_content = '''
"[project]/Config/DefaultEngine.ini" "../../../BeyondStar/Config/DefaultEngine.ini" -compress
"[project]/Config/Android/AndroidEngine.ini" "../../../BeyondStar/Config/Android/AndroidEngine.ini" -compress
"[project]/Config/IOS/IOSEngine.ini" "../../../BeyondStar/Config/IOS/IOSEngine.ini" -compress
"[project]/Config/DefaultScalability.ini" "../../../BeyondStar/Config/DefaultScalability.ini" -compress
"[project]/Config/DefaultDeviceProfiles.ini" "../../../BeyondStar/Config/DefaultDeviceProfiles.ini" -compress
"[project]/Config/Android/AndroidScalability.ini" "../../../BeyondStar/Config/Android/AndroidScalability.ini" -compress
"[project]/Config/IOS/IOSScalability.ini" "../../../BeyondStar/Config/IOS/IOSScalability.ini" -compress
"[engine]/Config/BaseScalability.ini" "../../../Engine/Config/BaseScalability.ini" -compress
"[engine]/Config/BaseDeviceProfiles.ini" "../../../Engine/Config/BaseDeviceProfiles.ini" -compress
'''

# pak_config_cmd = '''
# D:\unrealengine\Engine\Binaries\Win64\UnrealPak.exe "D:/ka1_client/client/trunk/BeyondStar/Saved/HotPatcher/Paks/2024.10.29-16.00.00/Android_ASTC/2024.10.29-16.00.00_Android_ASTC_001_P.pak" -create="D:/ka1_client/client/trunk/BeyondStar/Saved/HotPatcher/Paks/2024.10.29-16.00.00/Android_ASTC/2024.10.29-16.00.00_Android_ASTC_001_P_PakCommands.txt" -AlignForMemoryMapping=0 -compress -compressionformats=Zlib -cryptokeys="D:/ka1_client/client/trunk/BeyondStar/Saved/HotPatcher/Crypto.json" -projectdir="D:/ka1_client/client/trunk/BeyondStar/" -enginedir="D:/unrealengine/Engine/" -platform=Android
# '''

class MainWapper:
    def __init__(self, func):
        self.func = func
    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        return result

def main(func):        
    return MainWapper(func)

class HistoryValue:
    def __init__(self, size = 10, init_value = None):
        self.size = size

        if init_value is None:
            self.history_value = []
        else:
            if isinstance(init_value, list) or isinstance(init_value, tuple) or isinstance(init_value, set):
                self.history_value = list(init_value)
            else:
                self.history_value = [init_value]

    def Update(self, value):
        if value not in self.history_value:
            self.history_value.append(value)
        else:
            self.history_value.remove(value)
            self.history_value.append(value)

        if len(self.history_value) > self.size:
            self.history_value.pop(0)

    def __str__(self):
        # serialize to string buffer
        buffer = io.StringIO()
        # buffer.write('')
        for i in self.history_value:
            buffer.write(str(i))
            buffer.write('\n')
        return buffer.getvalue()
    
    def ConvertFromString(self, string):
        self.history_value = []
        for line in string.split('\n'):
            if line:
                self.Update(line)


class Config:
    '''
    把一些使用状态保存到注册表
    '''
    def __init__(self, key = r"Software\MyUtility"):
        self.reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)        

        try:
            self.key = winreg.OpenKeyEx(self.reg, key, access=winreg.KEY_ALL_ACCESS)
            
        except FileNotFoundError:
            self.key = winreg.CreateKeyEx(self.reg, key, access=winreg.KEY_ALL_ACCESS)

        self.cache = {}
        

    def get(self, name, default=None):
        value_type = type(default)
        try:
            value, _ = winreg.QueryValueEx(self.key, name)
            return value_type(value)
        except FileNotFoundError:
            return value_type(default)

    def set(self, name, value):
        try:
            winreg.SetValueEx(self.key, name, 0, winreg.REG_SZ, str(value))
        except Exception as e:
            print(e)

    def update(self, name, value):
        self.cache[name] = value


    def save(self):
        for key, value in self.cache.items():
            self.set(key, value)

        winreg.CloseKey(self.key)
        winreg.CloseKey(self.reg)


class PopupWindow():
    def __init__(self, parent, title=""):
        self.parent = parent
        self.window = Toplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        
        self.text_widget = Text(self.window, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.button_copy = Button(self.window, text="Copy", width=100, command=self.copy_text)
        self.button_copy.pack(pady=5)

    def copy_text(self):
        text = self.text_widget.get("1.0", tk.END)
        pyperclip.copy(text)
    
    def set_text(self, text):
        '''
        set multi-line text
        '''
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert(tk.END, text)





#打开temp目录下的renderdoc目录
def open_renderdoc():
    os.system("start renderdoc.exe")


class Utility:   

    apk_dir = r'D:\ka1_client\client\trunk\BeyondStar\Saved\HotPatcher\Paks'

    @staticmethod
    def find_newest_pak_file():
            
        # os.chdir()
        sub_dirs = os.listdir(Utility.apk_dir)
        modify_time = []
        for dir in sub_dirs:
            dir_name = f'{Utility.apk_dir}\\{dir}'
            print(dir_name)
            modify_time.append(os.path.getmtime(dir_name))        

        max_index = modify_time.index(max(modify_time))
        dir_name = sub_dirs[max_index]

        pak_name = f'{Utility.apk_dir}/{dir_name}/Android_ASTC/{dir_name}_Android_ASTC_001_P.pak'
        if not os.path.exists(pak_name):
            messagebox.showwarning(None, f"{pak_name} not exist!")
            return
        
        return pak_name

    @staticmethod
    def copy_latest_apk(target_dir : str = 'd:\\'):
        directory = r'\\nas.ka60om.com\package\trunk\Android_ASTC\base\android_internal'

        apk_files = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.apk'):
                    file_path = os.path.join(root, file)
                    modify_time = os.path.getmtime(file_path)
                    apk_files.append((file_path, modify_time))
                    # print(file_path, modify_time)
        
        if len(apk_files) == 0:
            messagebox.showwarning(None, "found no apk files")
            return
        
        latest_file = max(apk_files, key=lambda x: x[1])[0]

        if messagebox.askokcancel("", f"copy {latest_file} to {target_dir} ?") :            
            shutil.copy(latest_file, target_dir)
            file_path = os.path.join(target_dir, os.path.basename(latest_file))
            subprocess.Popen(f'explorer /select,"{file_path}"')
            # print(f'copy {latest_file} to {target_dir}')


    @staticmethod
    def make_temp_filename():
        return tempfile.mktemp()
    
    @staticmethod
    def open_pak_dir():
        os.system(f'explorer "{Utility.apk_dir}"')


    @staticmethod
    def create_pak_with_files(files, output_pak_name):

        pack_too_path = r'D:/unrealengine/Engine/Binaries/Win64/UnrealPak.exe'
        project_dir = r'D:/ka1_client/client/trunk/BeyondStar/'
        engine_dir = r'D:/unrealengine/Engine/'


        if len(files) == 0:
            messagebox.showwarning(None, "no files to pack")
            return

        # create temp file
        temp_file = tempfile.mktemp('.txt')
        with open(temp_file, 'w') as f:
            f.write(f'{files}\n')

        print(f'write temp file {temp_file}')

        #  -projectdir="D:/ka1_client/client/trunk/BeyondStar/" -enginedir="D:/unrealengine/Engine/" -platform=Android

        # create pak
        cmd = f'{pack_too_path} "{output_pak_name}" -create="{temp_file}" -AlignForMemoryMapping=0 -compress -compressionformats=Zlib'
        # print(cmd)
        result = os.system(cmd)

        # delete temp file
        os.remove(temp_file)

        if result != 0:
            messagebox.showwarning(None, "create pak failed")
            
        return result


class DefaultLogger:
    def __init__(self):
        pass

    def __call__(self, *args):
        print(*args)


class AdbConnection:
    def __init__(self, apk_path, project_name = "", port=""):

        self.logger = DefaultLogger()

        self.apk_path = apk_path
        self.package_name = self.try_to_get_package_name(project_name)

        assert self.package_name is not None, "can not get package name, please check project name"

        self.logger('package_name ', self.package_name)

        self.port = port
        if len(port) > 0:
            self.conection_string = f'-s 127.0.0.1:{port}'
        else:
            self.conection_string = ""
        
        self.project_name = project_name

        self.console_flags = {}

        # self.project_path = f'/sdcard/UE4Game/{self.project_name}/{self.project_name}'
        self.project_path = self.find_project_path()

        # self.process_name = 'com.kaboom.beyondstar.trunk'

        # self.device_list = self.execute_adb_command('devices')
        # print(self.device_list)

        self.connect_state = self.fetch_device_info()

    def get_connection_info(self):
        if self.connect_state:
            return f'{self.devices_brand} {self.devices_model}'
        
        else:
            return 'not connected'

    def find_project_path(self):
        try:
            candidata_path = f'/data/data/{self.package_name}/files/UE4Game/{self.project_name}/{self.project_name}'
            result = self.execute_adb_command(f"shell run-as {self.package_name} ls {candidata_path}/Saved/Logs")
            if result != 0:
                candidata_path = f'/sdcard/Android/data/{self.package_name}/files/UE4Game/{self.project_name}/{self.project_name}'
                result = self.execute_adb_command(f"shell run-as {self.package_name} ls {candidata_path}/Saved/Logs")

                if result != 0:
                    result = self.execute_adb_command(f"shell ls {candidata_path}/Saved/Logs")

                assert result == 0, f'can not find project path {candidata_path}'

            self.logger(f"found project path {candidata_path}")

            return candidata_path
        except Exception as e:
            self.logger(str(e))
            return None
    
    def execute_adb_command(self, command : str, use_subprocess=False):
        self.logger(command)

        if use_subprocess:
            cmds = command.split(" ")
            # print('cmds', cmds)
            result = subprocess.check_output(['adb', *cmds], shell=True)
            result = result.decode("utf-8")
            self.logger(result)
            return result
        else:

            result = os.system(f"adb {command}")
            return result
        # result = subprocess.call(['adb', command], text=True)
        # return result

    def try_to_get_package_name(self, key_word : str):
        '''
        获取正确的进程名,(带trunk或者不带trunk)
        '''
        # try:
        #     result = subprocess.check_output(f'adb shell \"ps -A -o NAME | grep {key_word.lower()}\"', shell=True)
        #     result = result.decode('utf-8')
        #     result = result.splitlines()
        #     if len(result) > 0 and len(result[0]) > 0:
        #         process_name = result[0].strip()
        #         return process_name
        # except:
        #     pass
        
        # return None

        activity_names = ['com.tencent.dhm1', 'com.kaboom.BeyondStar', 'com.kaboom.beyondstar.trunk', 'com.kaboom.beyondstar.ob', 'com.kaboom.beyondstar.obn']

        for activity_name in activity_names:
            
            result = self.execute_adb_command(f'shell run-as {activity_name} ls')
            if result == 0:
                return activity_name

        raise Exception('can not find package name')
    
        # result = self.execute_adb_command('shell run-as com.kaboom.BeyondStar ls')
        # if result == 0:
        #     return 'com.kaboom.BeyondStar'
        
        
        # result = self.execute_adb_command('shell run-as com.kaboom.beyondstar.trunk ls')
        # if result == 0:
        #     return 'com.kaboom.beyondstar.trunk'
        
        
        # result = self.execute_adb_command('shell run-as com.kaboom.beyondstar.ob ls')
        # if result == 0:
        #     return 'com.kaboom.beyondstar.trunk'

        # else:
        #     return 'com.kaboom.beyondstar.trunk'
        
    def start_process(self):
        self.execute_adb_command(f'{self.conection_string} shell am start -n {self.package_name}/com.epicgames.ue4.GameActivity')

    def stop_process(self):
        self.execute_adb_command(f'{self.conection_string} shell am force-stop {self.package_name}')

    def get_adb_meminfo(self):
        '''
        fetch android meminfo
        '''
        result = subprocess.check_output(f'adb shell dumpsys meminfo {self.package_name}', shell=True)
        result = result.decode('utf-8')
        return result

    def fetch_device_info(self):
        try:
            result = subprocess.check_output('adb shell getprop ro.product.model', shell=True)
            self.devices_model = result.decode('utf-8').strip()

            result = subprocess.check_output('adb shell getprop ro.product.manufacturer', shell=True)
            self.devices_manufacturer = result.decode('utf-8').strip()        

            result = subprocess.check_output('adb shell getprop ro.product.brand', shell=True)
            self.devices_brand = result.decode('utf-8').strip()

            self.logger('device info', self.devices_model, self.devices_manufacturer, self.devices_brand)

            return True
        except:
            
            return False
    


    def connect_adb(self):
        if len(self.port) > 0:
            self.execute_adb_command(f'connect 127.0.0.1:{self.port}')

    def install_apk(self):
        res = self.execute_adb_command(f'{self.conection_string} install {self.apk_path}')
        self.logger(res)

    def list_devices(self):
        res = self.execute_adb_command('devices', use_subprocess=True)
        self.logger(res)

    def connnect_device(self, ip_address):
        res = self.execute_adb_command(f'connect {ip_address}', use_subprocess=True)
        self.logger(res)

    def remove_apk(self):
        res = self.execute_adb_command(f'{self.conection_string} uninstall {self.package_name}')
        self.logger(res)

    def fetch_log_file(self):
        
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_file_name = f'{tempfile.gettempdir()}\\{self.project_name}_{now}.log'
        self.logger('temp file ', temp_file_name)      

        self.execute_adb_command(f'{self.conection_string} pull {self.project_path}/Saved/Logs/{self.project_name}.log {temp_file_name}')
        os.system(temp_file_name)

    def console_command(self, command : str):
        self.execute_adb_command(f'{self.conection_string} shell \"am broadcast -a android.intent.action.RUN -e cmd \'{command}\'\"')

    def send_file_to_pck(self, file_path : str):
        self.execute_adb_command(f'{self.conection_string} push {file_path} {self.project_path}/Saved/pck/')

    def remove_lua_file(self, file_path : str):
        base_file_name = os.path.basename(file_path)
        print('base file ', base_file_name)
        self.execute_adb_command(f'{self.conection_string} shell rm {self.project_path}/Saved/pck/{base_file_name}')

    def toggle_flag(self, flag_name : str):
        flag = False
        if flag_name in self.console_flags:
            flag = not self.console_flags[flag_name]
            
        self.console_flags[flag_name] = flag

        value = 1 if flag else 0
        self.console_command(f'{flag_name} {value}')
        # self.execute_adb_command(f'{self.conection_string} shell \"am broadcast -a android.intent.action.RUN -e cmd \'{flag_name} {value}\'\"')

    def push_android_lua_file(self):
        # adb shell mkdir -p /sdcard/UE4Game/BeyondStar/BeyondStar/Saved/pck
        self.execute_adb_command(f'{self.conection_string} shell mkdir -p {self.project_path}/Saved/pck')

        content = '''
local PlatformConfig = _G.GPlatFormConfig
PlatformConfig.MaxFPS = 30
PlatformConfig.EnablePatcher = false
PlatformConfig.EnableDLC = true
PlatformConfig.PCKDir = ""
PlatformConfig.ContentDir = ""
'''
        # create temp file
        temp_file_name = 'android.lua'
        with open(temp_file_name, 'w', encoding='utf-8') as f:
            f.write(content)

        self.execute_adb_command(f'{self.conection_string} push {temp_file_name} {self.project_path}/Saved/pck/')

        os.remove(temp_file_name)

        self.restart_process()


    def restart_process(self):
            self.stop_process()
            time.sleep(0.5)
            self.start_process()

    def push_newest_pack_file(self):
        pak_file_name = Utility.find_newest_pak_file()
        if not pak_file_name:
            messagebox.showwarning(None, "not found pak file")
            return
        
        if messagebox.askokcancel(message=f"copy pak {pak_file_name}"):
            # adb shell rm /sdcard/UE4Game/BeyondStar/BeyondStar/Saved/Paks/*
            
            self.execute_adb_command(f'{self.conection_string} shell mkdir -p {self.project_path}/Saved/Paks/')
            self.execute_adb_command(f'{self.conection_string} push {pak_file_name} {self.project_path}/Saved/Paks/')
            # self.execute_adb_command(f'{self.conection_string} shell \"cp -f /mnt/sdcard/UE4Game/{self.project_name}/Content/Paks/* /sdcard/UE4Game/{self.project_name}/Content/Paks/\"')


    def delete_all_pack_file(self):
        self.execute_adb_command(f'{self.conection_string} shell rm {self.project_path}/Saved/Paks/*')

    
    pak_file_name = 'config_p.pak'

    def create_config_pak_and_push_to_device(self, to_paks_or_pck = True):
        
        pack_too_path = r'D:/unrealengine/Engine/Binaries/Win64/UnrealPak.exe'
        project_dir = r'D:/ka1_client/client/trunk/BeyondStar'
        engine_dir = r'D:/unrealengine/Engine'

        src_file_name = os.path.join('d:/', AdbConnection.pak_file_name).replace('\\', '/')
        print(src_file_name)

        files_to_pak = confg_pak_content.replace('[project]', project_dir).replace('[engine]', engine_dir)
        print('files to pak\n', files_to_pak)        

        result = Utility.create_pak_with_files(files_to_pak, src_file_name)
        if result != 0:
            self.logger('create config pak failed', result)
            return
        
        sub_dir = 'Paks' if to_paks_or_pck else 'pck'

        self.execute_adb_command(f'{self.conection_string} shell mkdir -p {self.project_path}/Saved/{sub_dir}/')
        result = self.execute_adb_command(f'{self.conection_string} push \"{src_file_name}\" {self.project_path}/Saved/{sub_dir}/')

        if result != 0:
            self.logger('push config pak failed', result)
            return
        
        if to_paks_or_pck:
            self.logger('push config pak success, retart process', result)
            self.stop_process()
            time.sleep(0.5)
            self.start_process()

        # elif messagebox.askokcancel(message=f"restart process?"):

        elif messagebox.askokcancel(message='reload pak?'):
            self.console_command(f'ExecMountPak {self.project_path}/Saved/{sub_dir}/{AdbConnection.pak_file_name} 0')
            # self.execute_adb_command(f'{self.conection_string} shell rm {self.project_path}/Saved/pck/{pak_file_name}')


    def remove_config_pak(self):
                
        self.execute_adb_command(f'{self.conection_string} shell rm {self.project_path}/Saved/Paks/{AdbConnection.pak_file_name}')
        self.execute_adb_command(f'{self.conection_string} shell rm {self.project_path}/Saved/pck/{AdbConnection.pak_file_name}')


    def fetch_memory_report_file(self):
        self.execute_adb_command(f'{self.conection_string} pull {self.project_path}/Saved/Logs/MemoryReport.log')

    def dump_memory_info(self):
        self.console_command('MemReport -Full')

        time.sleep(3)

        # find latest report file        
        result = subprocess.check_output(['adb', 'shell', 'find', f'{self.project_path}/Saved/Profiling/MemReports/', '-type', 'f'], shell=True)
        report_files = result.decode().splitlines()

        file_list = []
        for file in report_files:
            numbers = re.findall(r'\d\d', file)
            time_string = ''.join(numbers)
            file_list.append((time_string, file))

        latest_file = max(file_list, key=lambda x: x[0])[1]

        fetch_cmd = f'pull {latest_file} {tempfile.gettempdir()}'
        self.execute_adb_command(fetch_cmd)

        file_name = os.path.join(tempfile.gettempdir(), os.path.basename(latest_file))
        os.system(f'code {file_name}')

        
    def set_ue_commandline(self, command : str):
        # create temp file
        temp_file_name = 'UE4CommandLine.txt'
        with open(temp_file_name, 'w', encoding='utf-8') as f:
            f.write(command)

        self.logger(temp_file_name, self.project_path)
        file_path = self.project_path.rsplit('/', 1)[0]
        self.logger(file_path)

        self.execute_adb_command(f'{self.conection_string} push {temp_file_name} {file_path}/')        
        os.remove(temp_file_name)
        
        # self.execute_adb_command(f'{self.conection_string} shell \"echo \'{command}\' > {file_path}/UE4CommandLine.txt\"')

    def remove_ue_commandline(self):
        
        file_path = self.project_path.rsplit('/', 1)[0]
        self.execute_adb_command(f'{self.conection_string} shell rm {file_path}/UE4CommandLine.txt')

    def debug_commandline(self):
        file_path = self.project_path.rsplit('/', 1)[0]
        a = []
        # remove empty element

        output = self.execute_adb_command(f'{self.conection_string} shell cat {file_path}/UE4CommandLine.txt')
        self.logger(output)

    def disconnect(self):
        pass

    staticmethod
    def extract_pak_from_apk(file_path : str):
        if not os.path.exists(file_path):
            print(f'{file_path} not exists')
            return
        
        path = os.path.dirname(file_path)

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            png_file_name = 'assets/main.obb.png'
            try:
                info = zip_ref.getinfo(png_file_name)
                # print(info)
            except KeyError:
                print(f'{png_file_name} not found')
                return
            
            # pak_file_path = zip_ref.extract(info, path)
            # print(f'extract {pak_file_path} success')

            png_file_obj = zip_ref.open(info)
            assert png_file_obj is not None

            with zipfile.ZipFile(png_file_obj, 'r') as png_file:
                pak_file_name = 'BeyondStar/Content/Paks/BeyondStar-Android_ASTC.pak'
                try:
                    info = png_file.getinfo(pak_file_name)
                    # print(info)
                except KeyError:
                    print(f'{pak_file_name} not found')
                    return
                
                
                out_file_name = os.path.splitext(os.path.basename(file_path))[0]
                out_file_name = os.path.join(path, out_file_name + ".pak")

                zip_pak_file = png_file.open(info)
                with open(out_file_name, 'wb') as f:
                    while True:
                        chunk = zip_pak_file.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)

                # pak_file_path = png_file.extract(info, path)
                print(f'extract {out_file_name} success')

                # file_name = os.path.basename(file_name)
                # new_file_name = os.path.join(path, AdbConnection.pak_file_name)

            





# derive from AdbConnection
class SocketConnection(AdbConnection):
    def __init__(self, host):
        print(f'init socket connection {host}')

        self.host = host
        self.port = 8888
        self.connect_state = self.connect()


    def connect(self):
        succeeded = False
        server_ip = self.host
        server_port = self.port
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        

        try:
            client_socket.connect((server_ip, server_port))
            succeeded = True

            self.socket = client_socket

        except socket.error as e:
            print("连接服务器出错:", e)

        return succeeded
    
    def disconnect(self):
        if not self.connect_state:
            return
        
        self.socket.close()
        self.socket = None
        self.connect_state = False


    def execute_adb_command(self, command : str, use_subprocess=False):
        return 0
    
    
    def console_command(self, command : str):
        if not self.connect_state:
            print('console_command : socket not connected')
            return

        try:
            self.socket.send(command.encode('utf-8'))
        except socket.error as e:
            print("发送命令出错:", e)    
    
    def get_connection_info(self):
        if self.connect_state:
            return 'socket connected'
        
        else:
            return 'socket not connected'


class PerforceUtility:
    logger = DefaultLogger()

    def __init__(self):
        pass

    staticmethod
    def force_update(file):        
        result = subprocess.check_output(f"p4 sync -f {file}")
        result = result.decode('utf-8')

        return result

    @staticmethod
    def force_update_clipboard():
        text : str = pyperclip.paste()
        lines = text.splitlines()

        string_buffer = io.StringIO()

        count = 0
        for line in lines:
            line = line.strip()
            if not line.startswith("//"):
                print(r'update info should start with //')
                break
            
            result : re.Match = re.match(r'.* can\'t update modified file (.*)', line)
            if result:
                file = result.group(1)
                # print('matched', file)
                result = PerforceUtility.force_update(file)
                string_buffer.write(f'{result}\n')
                count += 1

        PerforceUtility.logger(string_buffer.getvalue())
        # popup = PopupWindow(None, "Perforce Update")
        # popup.set_text(string_buffer.getvalue())
        # print(f"update {count} files")

        return count
            



# def button_install_click():
#     # 示例：获取设备列表
#     device_list = execute_adb_command('devices')
#     print(device_list)

class ToggleButtonHelper:
    def __init__(self, func, variable : tk.BooleanVar = None):
        if not variable:
            self.variable = tk.BooleanVar()
        else:
            self.variable =  variable

        self.func = func
        
    def __call__(self):
        self.func(self.variable.get())


class ComboHelper:
    def __init__(self, widget : Combobox, func, config = None):
        assert widget
        assert func

        self.widget = widget
        self.func = func
        self.config = config

        if config:
            name = self.widget.winfo_name()
            assert name != ''
            self.widget.current(config.get(name, 0))

    def __call__(self, event):
        value = self.widget.get()
        self.func(value)

        if self.config:
            name = self.widget.winfo_name()
            sel_index = self.widget.current()
            if sel_index != -1:
                self.config.update(name, sel_index)


class Window:

    class Logger:
        def __init__(self, text_widget : tk.Text):
            self.text_widget = text_widget

        def __call__(self, *args):
            self.text_widget.config(state=tk.NORMAL)
            
            if type(args) == list:
                args = ''.join(args)
            else:
                args = str(args)

            self.text_widget.insert('end', args + '\n')
            self.text_widget.config(state=tk.DISABLED)



    def __init__(self, connect_info):
        self.root = Tk()
        self.connect_info = connect_info
        self.connection = None
        self.config = Config()

        self.logger = DefaultLogger()

        self.create_window_frame()

        PerforceUtility.logger = self.logger

    def on_closing(self):
        # if messagebox.askokcancel("退出", "你想要退出吗?"):

        if self.connection:
            self.connection.disconnect()

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        x = self.root.winfo_x()
        y = self.root.winfo_y()

        self.config.set("window_rect", f"{width}x{height}+{x}+{y}")
        self.config.save()
        self.logger("config saved")

        self.root.destroy()

    # def log(self, *text):
    #     self.log_widget.config(state=tk.NORMAL)
    #     self.log_widget.insert(tk.END, ' '.join(text) + '\n')
    #     self.log_widget.insert(tk.END, ' '.join(text) + '\n')
    #     self.log_widget.config(state=tk.DISABLED)
        

    def on_tab_change(self, event):
        index = self.notebook.index(self.notebook.select())
        self.config.update("current_tab", index)

        # print("Tab changed to:", self.notebook.tab(event.widget.select(), "text"))

    def setup_grid_layout(self, widget : tk.Widget, row, column, rowspan=1, columnspan=1, sticky="nsew"):
        pad = 4
        widget.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, padx=pad, pady=pad, sticky=sticky)
        return (row, column + columnspan)

    def show_memory_info(self):
        info = self.connection.get_adb_meminfo()
        popup = PopupWindow(self.root, "Memory Info")
        popup.set_text(info)

    def connect_by_adb(self, target_info, result_info : tk.StringVar):
        self.connection = AdbConnection(**target_info)
        result_info.set(f'连接状态 : {self.connection.get_connection_info()}')

    def connect_by_socket(self, target_info, result_info : tk.StringVar):
        
        self.connection = SocketConnection(target_info)
        result_info.set(f'连接状态 : {self.connection.get_connection_info()}')

    def extract_pak_from_apk(self):
        print("extract pak from apk")
        file_name = filedialog.askopenfilename(title="选择文件", filetypes=[("apk file", "*.apk"), ("all files", "*.*")])
        
        if file_name:
            AdbConnection.extract_pak_from_apk(file_name)
        
    def create_window_frame(self):
        self.root.title("Utility")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        style = {
                'background': '#E0E0E0',
                # 'borderwidth': 1,
                'relief': tk.SOLID,
                'highlightthickness' : 1, 
                'highlightbackground' : "grey"
                #'font': ('Helvetica', 12)
            }

        grid_minsize = (100, 50)
        grid_pad = 6
        

        # 设置窗口大小
        self.root.geometry(self.config.get("window_rect", "800x600+1000+550"))

        ########### device info
        
        info_frame_pad = 6
        top_frame = Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        top_frame.columnconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=grid_minsize[0], pad=grid_pad)
        top_frame.rowconfigure([0], weight=1, minsize=grid_minsize[1], pad=grid_pad)

        grid_column = 0
        self.device_info = tk.StringVar()
        button_connect = Button(master=top_frame, text="连接adb", command=lambda : self.connect_by_adb(self.connect_info, self.device_info), **style)
        button_connect.grid(row=0, column=grid_column, sticky="nsew", padx=info_frame_pad, pady=info_frame_pad)
        grid_column += 1

        combo_connecion_ip = Combobox(top_frame, values=["10.0.210.173", "10.0.210.25", "10.0.210.27"], justify='right', name='combo_connecion_ip')
        combo_connecion_ip.grid(row=0, column=grid_column, sticky="nsew", padx=info_frame_pad, pady=info_frame_pad)
        combo_connecion_ip.current(0)
        grid_column += 1

        button_connect_socket = Button(master=top_frame, text="连接socket", command=lambda : self.connect_by_socket(combo_connecion_ip.get(), self.device_info), **style)
        button_connect_socket.grid(row=0, column=grid_column, sticky="nsew", padx=info_frame_pad, pady=info_frame_pad)
        grid_column += 1

        lable_device = Label(top_frame, textvariable=self.device_info)
        lable_device.grid(row=0, column=grid_column, sticky="nsew", padx=info_frame_pad, pady=info_frame_pad)

        self.connect_by_adb(self.connect_info, self.device_info)
        
        ############## 

        self.notebook = Notebook(self.root)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.notebook.pack(fill=tk.BOTH, expand=True)

        # log widget
        bottom_frame = Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        log_widget = Text(bottom_frame, height=10)
        log_widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        log_widget.config(state=tk.DISABLED)
        self.logger = Window.Logger(log_widget)
        self.connection.logger = self.logger

        tab1 = Frame(self.notebook)
        tab1.columnconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=grid_minsize[0], pad=grid_pad)
        tab1.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7], weight=1, minsize=grid_minsize[1], pad=grid_pad)
        self.notebook.add(tab1, text="base")        

        current_row = 0
        current_column = 0

        # button_connect = Button(master=tab1, text="连接", command=lambda : self.connection.connect_adb())
        # current_row, current_column = self.setup_grid_layout(button_connect, current_row, current_column)

        # button_install = Button(tab1, text="安装", command= lambda : self.connection.install_apk())
        # current_row, current_column = self.setup_grid_layout(button_install, current_row, current_column)

        # button_remove = Button(tab1, text="卸载", command=lambda : self.connection.remove_apk())
        # current_row, current_column = self.setup_grid_layout(button_remove, current_row, current_column)        

        button_push_android_lua = Button(tab1, text="推送android.lua", command=lambda : self.connection.push_android_lua_file(), **style)
        current_row, current_column = self.setup_grid_layout(button_push_android_lua, current_row, current_column)

        button_fetch_log = Button(tab1, text="获取日志", command=lambda : self.connection.fetch_log_file(), **style)
        current_row, current_column = self.setup_grid_layout(button_fetch_log, current_row, current_column)

        button_push_pak = Button(tab1, text="推送最新pak", command=lambda : self.connection.push_newest_pack_file(), **style)
        current_row, current_column = self.setup_grid_layout(button_push_pak, current_row, current_column)

        button_delete_pak = Button(tab1, text="删除(手机)所有pak", command=lambda : self.connection.delete_all_pack_file(), **style)
        current_row, current_column = self.setup_grid_layout(button_delete_pak, current_row, current_column)

        button_open_pak_dir = Button(tab1, text="打开pak目录", command=lambda : Utility.open_pak_dir(), **style)
        current_row, current_column = self.setup_grid_layout(button_open_pak_dir, current_row, current_column)

        current_row, current_column = current_row + 1, 0
        
        
        send_lua_file_var = tk.StringVar()
        send_lua_file_var.set(self.config.get('send_lua_file', ''))
        current_row, current_column = self.setup_grid_layout(Entry(tab1, textvariable=send_lua_file_var), current_row, current_column, columnspan=4)

        on_send_lua_command = lambda : (self.connection.send_file_to_pck(send_lua_file_var.get()), self.config.update('send_lua_file', send_lua_file_var.get()))
        button_send_lua_file = Button(tab1, text="send lua file", command=on_send_lua_command, **style)
        current_row, current_column = self.setup_grid_layout(button_send_lua_file, current_row, current_column)

        button_remove_lua_files = Button(tab1, text="remove lua file", command=lambda : self.connection.remove_lua_file(send_lua_file_var.get()), **style)
        current_row, current_column = self.setup_grid_layout(button_remove_lua_files, current_row, current_column)

        current_row, current_column = current_row + 1, 0

        button_create_config_pak = Button(tab1, text="create config pak (to paks)", command=lambda : self.connection.create_config_pak_and_push_to_device(), **style)
        current_row, current_column = self.setup_grid_layout(button_create_config_pak, current_row, current_column)
        
        button_create_config_pck = Button(tab1, text="create config pak (to pck)", command=lambda : self.connection.create_config_pak_and_push_to_device(to_paks_or_pck=False), **style)
        current_row, current_column = self.setup_grid_layout(button_create_config_pck, current_row, current_column)

        button_remove_config_pak = Button(tab1, text="remove config pak", command=lambda : self.connection.remove_config_pak(), **style)
        current_row, current_column = self.setup_grid_layout(button_remove_config_pak, current_row, current_column)

        ############# tab 2 ###############
        
        tab2 = Frame(self.notebook)

        tab2.columnconfigure([0, 1, 2, 3, 4, 5, 6], weight=1, minsize=grid_minsize[0], pad=grid_pad)
        tab2.rowconfigure([0, 1, 2, 3, 4, 5, 6, 7], weight=1, minsize=grid_minsize[1], pad=grid_pad)

        self.notebook.add(tab2, text="console command")
        current_row = 0
        current_column = 0

        button_show_fps = Button(tab2, text="show fps", command=lambda : self.connection.console_command("stat fps"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_fps, current_row, current_column)

        button_stat_unit = Button(tab2, text="stat unit", command=lambda : self.connection.console_command("stat unit"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_unit, current_row, current_column)

        button_stat_game = Button(tab2, text="stat game", command=lambda : self.connection.console_command("stat game"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_game, current_row, current_column)

        button_stat_engine = Button(tab2, text="stat engine", command=lambda : self.connection.console_command("stat engine"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_engine, current_row, current_column)

        button_stat_tickgroups = Button(tab2, text="stat tickgroups", command=lambda : self.connection.console_command("stat tickgroups"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_tickgroups, current_row, current_column)

        button_stat_anim = Button(tab2, text="stat anim", command=lambda : self.connection.console_command("stat anim"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_anim, current_row, current_column)

        current_row, current_column = current_row + 1, 0
        
        button_stat_initviews = Button(tab2, text="stat initviews", command=lambda : self.connection.console_command("stat initviews"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_initviews, current_row, current_column)

        button_stat_scenerendering = Button(tab2, text="stat scenerendering", command=lambda : self.connection.console_command("stat scenerendering"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_scenerendering, current_row, current_column)

        button_stat_particle = Button(tab2, text="stat particle", command=lambda : self.connection.console_command("stat ParticlesOverview"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_particle, current_row, current_column)

        button_stat_RHI = Button(tab2, text="stat RHI", command=lambda : self.connection.console_command("stat RHI"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_RHI, current_row, current_column)

        button_stat_Niagara = Button(tab2, text="stat Niagara", command=lambda : self.connection.console_command("stat Niagara"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_Niagara, current_row, current_column)

        button_stat_slate = Button(tab2, text="stat slate", command=lambda : self.connection.console_command("stat slate"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_slate, current_row, current_column)
        
        current_row, current_column = current_row + 1, 0
        button_stat_component = Button(tab2, text="stat component", command=lambda : self.connection.console_command("stat component"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_component, current_row, current_column)

        button_stat_canvas = Button(tab2, text="stat canvas", command=lambda : self.connection.console_command("stat canvas"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_canvas, current_row, current_column)

        button_stat_LLM = Button(tab2, text="stat LLM", command=lambda : self.connection.console_command("stat LLM"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_LLM, current_row, current_column)

        button_stat_LLMFULL = Button(tab2, text="stat LLMFULL", command=lambda : self.connection.console_command("stat LLMFULL"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_LLMFULL, current_row, current_column)

        button_stat_LLMPlatform = Button(tab2, text="stat LLMPlatform", command=lambda : self.connection.console_command("stat LLMPlatform"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_LLMPlatform, current_row, current_column)

        button_stat_slg = Button(tab2, text="stat slg", command=lambda : self.connection.console_command("stat slg"), **style)
        current_row, current_column = self.setup_grid_layout(button_stat_slg, current_row, current_column)

        current_row, current_column = current_row + 1, 0
        button_dump_memory = Button(tab2, text="dump memory", command=lambda : self.connection.dump_memory_info(), **style)
        current_row, current_column = self.setup_grid_layout(button_dump_memory, current_row, current_column)

        button_get_adb_memeory = Button(tab2, text="get adb meminfo", command=lambda : self.show_memory_info(), **style)
        current_row, current_column = self.setup_grid_layout(button_get_adb_memeory, current_row, current_column)

        button_toggle_rendering = Button(tab2, text="toggle rendering", command=lambda : self.connection.toggle_flag("ShowFlag.Rendering"), **style)
        current_row, current_column = self.setup_grid_layout(button_toggle_rendering, current_row, current_column)

        button_freeze_frame = Button(tab2, text="freeze frame", command=lambda : self.connection.console_command("FreezeFrame"), **style)
        current_row, current_column = self.setup_grid_layout(button_freeze_frame, current_row, current_column)

        button_toggle_planner_reflection = Button(tab2, text="toggle planner reflection", command=lambda : self.connection.toggle_flag("r.PlanarReflectionQuality"), **style)
        current_row, current_column = self.setup_grid_layout(button_toggle_planner_reflection, current_row, current_column)

        current_row, current_column = current_row + 1, 0

        button_show_postprocess = Button(tab2, text="show postprocess", command=lambda : self.connection.toggle_flag("ShowFlag.PostProcessing"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_postprocess, current_row, current_column)

        button_show_shadow = Button(tab2, text="show shadow", command=lambda : self.connection.toggle_flag("ShowFlag.DynamicShadows"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_shadow, current_row, current_column)

        button_show_staticmesh = Button(tab2, text="show staticmesh", command=lambda : self.connection.toggle_flag("ShowFlag.StaticMeshes"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_staticmesh, current_row, current_column)

        button_show_SkeletalMeshes = Button(tab2, text="show SkeletalMeshes", command=lambda : self.connection.toggle_flag("ShowFlag.SkeletalMeshes"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_SkeletalMeshes, current_row, current_column)

        button_show_transparency = Button(tab2, text="show transparency", command=lambda : self.connection.toggle_flag("ShowFlag.Translucency"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_transparency, current_row, current_column)

        
        button_show_particles = Button(tab2, text="show particles", command=lambda : self.connection.toggle_flag("ShowFlag.Particles"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_particles, current_row, current_column)

        button_show_Niagara = Button(tab2, text="show Niagara", command=lambda : self.connection.toggle_flag("ShowFlag.Niagara"), **style)
        current_row, current_column = self.setup_grid_layout(button_show_Niagara, current_row, current_column)

        current_row, current_column = current_row + 1, 0

        lable = Label(tab2, text="scale factor")
        current_row, current_column = self.setup_grid_layout(lable, current_row, current_column)
        combo_scale_factor = Combobox(tab2, values=["1.25", "1.0", "1.1", "1.5", '0', "0.8", "0.9"], justify='right', name='content_scale_factor')        
        current_row, current_column = self.setup_grid_layout(combo_scale_factor, current_row, current_column)
        helper = ComboHelper(combo_scale_factor, func=lambda x: self.connection.console_command(f"r.MobileContentScaleFactor {x}"), config=self.config)
        combo_scale_factor.bind("<<ComboboxSelected>>", helper)
        combo_scale_factor.bind('<Return>', helper)

        lable = Label(tab2, text="screen percentage")
        current_row, current_column = self.setup_grid_layout(lable, current_row, current_column)
        combo_screen_percentage = Combobox(tab2, values=["100", "120", "90", "110", "80", "70"], justify='right', name='screen_percentage')
        current_row, current_column = self.setup_grid_layout(combo_screen_percentage, current_row, current_column)
        helper = ComboHelper(combo_screen_percentage, func=lambda x: self.connection.console_command(f"r.ScreenPercentage {x}"), config=self.config)
        combo_screen_percentage.bind("<<ComboboxSelected>>", helper)
        combo_screen_percentage.bind('<Return>', helper)
        
        lable = Label(tab2, text="set fps")
        current_row, current_column = self.setup_grid_layout(lable, current_row, current_column)
        combo_max_fps = Combobox(tab2, values=["30", "60"], justify='right', name='max_fps')
        current_row, current_column = self.setup_grid_layout(combo_max_fps, current_row, current_column)
        helper = ComboHelper(combo_max_fps, func=lambda x: self.connection.console_command(f"t.maxfps {x}"), config=self.config)
        combo_max_fps.bind("<<ComboboxSelected>>", helper)
        combo_max_fps.bind('<Return>', helper)

        # button_set_near_plane = Button(tab2, text="set near plane", command=lambda : self.connection.console_command("r.SetNearClipPlane 100"))
        # current_row, current_column = self.setup_grid_layout(button_set_near_plane, current_row, current_column)

        current_row, current_column = current_row + 1, 0
        button_warfare = Button(tab2, text="warfare", command=lambda : self.connection.console_command("warfare_PLUS"), **style)
        current_row, current_column = self.setup_grid_layout(button_warfare, current_row, current_column)

        button_clean_warfare = Button(tab2, text="clean warfare", 
                                      command=lambda : (self.connection.console_command("kill_all_monsters"), 
                                                        self.connection.console_command("msg_setDmgRatio 1")), **style)
        current_row, current_column = self.setup_grid_layout(button_clean_warfare, current_row, current_column)

        toggler = ToggleButtonHelper(func = lambda b : self.connection.console_command("fogclear") if b else self.connection.console_command("fogresume"))
        button_clear_fog = Checkbutton(tab2, text="clear fog", variable=toggler.variable, command=toggler, indicatoron=False, **style)
        current_row, current_column = self.setup_grid_layout(button_clear_fog, current_row, current_column)

        current_row, current_column = current_row + 1, 0

        # s import "FlibPakHelper".MountPak(import "BlueprintPathsLibrary".ProjectSavedDir().."/xxx/xxx.pak", 0, "")
        
        lable = Label(tab2, text="other command")
        current_row, current_column = self.setup_grid_layout(lable, current_row, current_column)
        combo_other_command = Combobox(tab2, values=["r.RHIThread.Enable 0", "r.RHIThread.Enable 1", "r.ForceLOD 2", "r.ForceLOD -1", "tiny.DensityScale 0.5",
                                                     "dp.Override Android_ExtremeLow", "dp.Reload", "dp.ShowActiveProfile", "r.Mobile.EnableMovableSpotlightsMutable",
                                                     "ExecMountPak ../../../BeyondStar/Saved/pck/config_p.pak 0"], 
                                                     justify='left', name='other_command')
        current_row, current_column = self.setup_grid_layout(combo_other_command, current_row, current_column, columnspan=3)
        helper = ComboHelper(combo_other_command, func=lambda x: self.connection.console_command(x), config=self.config)
        combo_other_command.bind("<<ComboboxSelected>>", helper)
        combo_other_command.bind('<Return>', helper)

        # command_var = tk.StringVar()
        # command_var.set(self.config.get('last_command', ''))
        # input_command = Entry(tab2, textvariable=command_var)
        # current_row, current_column = self.setup_grid_layout(input_command, current_row, current_column, columnspan=4)

        # on_send_command = lambda : (self.connection.console_command(input_command.get()), self.config.update('last_command', input_command.get()))
        # button_send_command = Button(tab2, text="send cmd", command=on_send_command)
        # current_row, current_column = self.setup_grid_layout(button_send_command, current_row, current_column)
        
        current_row, current_column = current_row + 1, 0
        combo_ue_commandline = Combobox(tab2)                                                           # onethread
        combo_ue_commandline['values'] = ('-tracehost=127.0.0.1 -trace=CPU,RHICommands,RenderCommands,Slate,Animation,Bookmark,Frame,GPU', '-LLM', '-noperfthreads', '-ONETHREAD', '-ExecCmds=\"\"')

        saved_index = max(self.config.get('ue_commandline', 0), 0)
        combo_ue_commandline.current(saved_index)

        current_row, current_column = self.setup_grid_layout(combo_ue_commandline, current_row, current_column, columnspan=3)        
        # 
        local_cmd = lambda : (self.config.update('ue_commandline', combo_ue_commandline.current()), self.connection.set_ue_commandline(combo_ue_commandline.get()))
        button_send_command = Button(tab2, text="set ue commandline", command=local_cmd)
        current_row, current_column = self.setup_grid_layout(button_send_command, current_row, current_column)

        button_remove_command = Button(tab2, text="remove ue commandline", command=lambda : self.connection.remove_ue_commandline())
        current_row, current_column = self.setup_grid_layout(button_remove_command, current_row, current_column)

        button_debug_command = Button(tab2, text="debug command", command=lambda : self.connection.debug_commandline())
        current_row, current_column = self.setup_grid_layout(button_debug_command, current_row, current_column)

        #########################
        tab3 = Frame(self.notebook)
        current_row = 0
        current_column = 0

        tab3.columnconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=grid_minsize[0], pad=grid_pad)
        tab3.rowconfigure([0, 1, 2, 3, 4, 5], weight=1, minsize=grid_minsize[1], pad=grid_pad)

    
        connect_ip_var = tk.StringVar()
        connect_ip_var.set(self.config.get('connect_ip', ''))
        connect_ip_entry = Entry(tab3, textvariable=connect_ip_var)
        current_row, current_column = self.setup_grid_layout(connect_ip_entry, current_row, current_column, columnspan=3)

        button_connect_ip = Button(tab3, text="connect ip", command=lambda : (self.config.update('connect_ip', connect_ip_var.get()), self.connection.connnect_device(connect_ip_var.get())))
        current_row, current_column = self.setup_grid_layout(button_connect_ip, current_row, current_column)

        self.notebook.add(tab3, text="other")
        button_list_devices = Button(tab3, text="list devices", command=lambda : self.connection.list_devices(), **style)
        current_row, current_column = self.setup_grid_layout(button_list_devices, current_row, current_column)

        current_row, current_column = current_row + 1, 0
        button_update_p4 = Button(tab3, text="update p4 from clipboard", command=lambda : PerforceUtility.force_update_clipboard(), **style)
        current_row, current_column = self.setup_grid_layout(button_update_p4, current_row, current_column)

        button_copy_lated_apk = Button(tab3, text="copy latest apk", command=lambda : Utility.copy_latest_apk(), **style)
        current_row, current_column = self.setup_grid_layout(button_copy_lated_apk, current_row, current_column)

        current_row, current_column = current_row + 1, 0
        button_extract_pak_from_apk = Button(tab3, text="extract pak from apk", command=lambda : self.extract_pak_from_apk(), **style)
        current_row, current_column = self.setup_grid_layout(button_extract_pak_from_apk, current_row, current_column)

        self.notebook.select(self.config.get("current_tab", 0))


    def Main(self):
        self.root.mainloop()


# @main
def test():
    cmd = f'adb shell \"find /sdcard/Android/data/com.kaboom.beyondstar.trunk/files/UE4Game/BeyondStar/BeyondStar/Saved/Profiling/MemReports/ -type f\"'

    cmds = ['adb', 'shell', '\"find /sdcard/Android/data/com.kaboom.beyondstar.trunk/files/UE4Game/BeyondStar/BeyondStar/Saved/Profiling/MemReports/ -type f\"']

    # cmd2 = f'shell \"find /sdcard/Android/data/com.kaboom.beyondstar.trunk/files/UE4Game/BeyondStar/BeyondStar/Saved/Profiling/MemReports/ -type f\"'

    
    result = subprocess.check_output(['adb', 'shell', 'find', '/sdcard/Android/data/com.kaboom.beyondstar.trunk/files/UE4Game/BeyondStar/BeyondStar/Saved/Profiling/MemReports/', '-type', 'f'], shell=True)
    report_files = result.decode().splitlines()

    file_list = []
    for file in report_files:
        numbers = re.findall(r'\d\d', file)
        time_string = ''.join(numbers)
        file_list.append((time_string, file))

    latest_file = max(file_list, key=lambda x: x[0])[1]
    print(latest_file)

    

    # print(result)

    # os.system(cmd)


@main
def MainFrame():

    # connecton = AdbConnection(r"D:\dev\UINiagara\build\Android_ASTC\MyProject-Android-Debug-arm64.apk", 
    #                         project_name="MyProject", package_name="com.tencent.test", port="5655")

    # connecton = AdbConnection(r"D:\dev\UINiagara\build\Android_ASTC\MyProject-Android-Debug-arm64.apk", 
    #                         project_name="MyProject", package_name="com.tencent.test")

    # connecton = AdbConnection(r"D:\ka1_client\build\Android_ASTC\BeyondStar-arm64.apk", project_name="BeyondStar")
    # connecton.connect_adb()

    connect_info = {
        'apk_path' : r"D:\ka1_client\build\Android_ASTC\BeyondStar-arm64.apk", 
        'project_name' : "BeyondStar", 
        'port' : ""
    }


    main_window = Window(connect_info)
    main_window.Main()



def call_main():
    # file_name = r"D:\pak_size_analysis\BeyondStar-arm64_Development_450488_android_obn_internal_v0.45.0488.1_134_20250225_110909.apk"
    # AdbConnection.extract_pak_from_apk(file_name)

    # return

    current_module = inspect.getmodule(inspect.currentframe())

    callables = []
    for class_name, class_object in inspect.getmembers(current_module, inspect.isclass):
        for method_name, method_object in inspect.getmembers(class_object, lambda x: isinstance(x, MainWapper)):
            callables.append((class_name, method_object))

    class_objects = inspect.getmembers(current_module, lambda x: isinstance(x, MainWapper))
    for name, class_object in class_objects:
        assert type(class_object) == MainWapper
        callables.append((name, class_object))

    if len(callables) == 0:
        print("no main function found")
        return
    
    if len(callables) == 1:
        callables[0][1]()

    if len(callables) > 1:
        for index, callable in enumerate(callables):
            print(f"{index} : {callable[0]}")

        selected_index = int(input("select index: "))
        if selected_index >= 0 and selected_index < len(callables):
            callables[selected_index][1]()
        else:
            print("invalid index")


if __name__ == "__main__":
    call_main()