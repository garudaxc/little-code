import os
import os.path
import sys
import datetime



os.chdir(r'D:\ka1_client\client\trunk\BeyondStar\Saved\HotPatcher')
current = os.path.abspath('.')
# print(current)


dirs = os.listdir('./Paks')
modify_time = []
for pak_dir in dirs:
    dir_name = f'./Paks/{pak_dir}'
    modify_time.append(os.path.getmtime(dir_name))
    # os.path.getmtime()
    

max_index = modify_time.index(max(modify_time))
dir_name = dirs[max_index]

pak_name = f'Paks/{dir_name}/Android_ASTC/{dir_name}_Android_ASTC_001_P.pak'
if not os.path.exists(pak_name):
    print(pak_name, 'not exist!')
    exit(1)

print('found pak', pak_name)


cmd = f'adb push {pak_name} /sdcard/UE4Game/BeyondStar/BeyondStar/Saved/Paks'
os.system(cmd)
