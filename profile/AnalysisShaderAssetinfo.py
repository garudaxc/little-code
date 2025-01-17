import os
import sys
from os import path
import json
import re
import csv
import numpy as np


def ReadDumpInfo(file_name):
    with open(file_name, 'r') as file:
        line = file.readline()
        line = file.readline()
        line = file.readline()
        assert line.find('ShaderMapHashes') != -1
        line = file.readline()

        ShaderMapHashes = []
        line = file.readline()

        while line.find('}') == -1:
            line = line.strip()
            ShaderMapHashes.append(line)
            line = file.readline()

        while line.find('ShaderMapEntries') == -1:
            line = file.readline()
        
        line = file.readline()

        def ReadEntry():
            line = file.readline()
            if line.find('FShaderMapEntry') == -1:
                return -1
            
            line = file.readline()
            line = file.readline()
            line = file.readline()
            
            match = re.search('NumShaders : (\d+)', line)
            assert match != None

            NumShaders = int(match.group(1))
            assert NumShaders > 0
            
            line = file.readline()
            line = file.readline()
            line = file.readline()

            return NumShaders
        
        ShaderEntrys = []
        num_shader_in_entry = ReadEntry()
        while num_shader_in_entry > 0:
            ShaderEntrys.append(num_shader_in_entry)
            num_shader_in_entry = ReadEntry()
            

        # print('entry', len(ShaderEntrys))
        assert len(ShaderMapHashes) == len(ShaderEntrys)

        # print('ShaderMapHashes', len(ShaderMapHashes))

        return ShaderMapHashes, ShaderEntrys



# read shader asset info file
def ReadShaderAssetInfo(file_name, shader_dump_file, output_file):
    
    with open(file_name, 'r', encoding='UTF-8') as file:
        data = json.load(file)
        data = data['ShaderCodeToAssets']

        print(type(data), len(data), type(data[0]))

    AssetsItem = {}
    AssetsLevelCount = {}

    for item in data:
        hash = item['ShaderMapHash']
        AssetsItem[hash] = item['Assets']

        for id in item['Assets']:
            if id in AssetsLevelCount:
                AssetsLevelCount[id] += 1
            else:
                AssetsLevelCount[id] = 1

    print('items', len(AssetsItem))
    # for k, v in AssetsItem.items():
    #     print(v, k)

    ShaderMapHashes, ShaderEntrys = ReadDumpInfo(shader_dump_file)

    ShaderEntrys = np.array(ShaderEntrys)
    sort_index = np.argsort(ShaderEntrys)[::-1]

    shader_count_info = []
    has_added = set()
    for index in sort_index:
        hash = ShaderMapHashes[index]
        assert hash in AssetsItem

        assets = AssetsItem[hash]
        first_asset = assets[0]
        if not (first_asset in has_added):
            info = {}
            info['asset'] = first_asset
            info['num_shaders'] = ShaderEntrys[index]
            info['quality levels'] = AssetsLevelCount[first_asset]

            shader_count_info.append(info)

            has_added.add(first_asset)        

    print('items with quality level ', len(shader_count_info))
    try:

        with open(output_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile,  fieldnames = shader_count_info[0].keys(), lineterminator='\n')
            writer.writeheader()
            writer.writerows(shader_count_info)

        os.system(output_file)

    except:
        print(f'write file {output_file} failed!')



def Main():
        
    current_dir = path.dirname(__file__)
    os.chdir(current_dir)

    # print(__file__)
    # print(sys.argv)

    # print(current_dir)

    project_dir = r'D:\UINiagara\MyProject'
    project_dir = r'D:\ka1_client\client\trunk\BeyondStar'


    project_dir = project_dir.replace('\\', '/')
    pos = project_dir.rfind('/') + 1
    project_name = project_dir[pos:]

    print('project name', project_name)

    shader_asset_info_file = f'{project_dir}/Saved/Shaders/GLSL_ES3_1_ANDROID/ShaderAssetInfo-{project_name}-GLSL_ES3_1_ANDROID.assetinfo.json'
    print('shader asset info file', shader_asset_info_file)

    shader_dump_file = f'{project_dir}/Saved/Shaders/GLSL_ES3_1_ANDROID/ShaderDebug-{project_name}-GLSL_ES3_1_ANDROID/dump.txt'

    pipeline_cache_file = f'{project_dir}/Build/Android_ASTC/PipelineCaches/PipelineCache_dump.csv'

    output_file = f'{project_dir}/Saved/Shaders/GLSL_ES3_1_ANDROID/shader-count-in-shadermap-{project_name}.csv'

    ReadShaderAssetInfo(shader_asset_info_file, shader_dump_file, output_file)


if __name__ == '__main__':
    Main()