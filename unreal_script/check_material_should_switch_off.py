import unreal
import os
import sys
import importlib

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)

if 'unreal_utility' in sys.modules:
    importlib.reload(sys.modules['unreal_utility'])

import unreal_utility
import perforce_tool


# 骨骼模型上不应该使用开着instance animation的材质


def collect_material(mesh_asset):
    material_list = []
    mesh = mesh_asset.get_asset()
    materials = mesh.materials
    for material in materials:
        material_list.append(material.material_interface)
    return material_list


def get_root_material(material):
    while material and (not isinstance(material, unreal.Material)):
        material = material.parent
    
    return material


def CheckMaterialShouldSwitchOff(material):
    root = get_root_material(material)
    if not root:
        return False
    
    root_name = root.get_path_name()
    # if root_name == '/Game/Models/MaterialBases/MaterialMasters/MM_Soldier_Base_Simplelit.MM_Soldier_Base_Simplelit':
    if root_name == '/Game/Buildings/Materials/MaterialMasters/M_Facility_Simple.M_Facility_Simple':
        # param_names = unreal.MaterialEditingLibrary.get_static_switch_parameter_names(root)
        value = unreal.MaterialEditingLibrary.get_material_instance_static_switch_parameter_value(material, '启用instance animation')
        
        return value

    return False


def count_root_material(materials):

    root_materials = set()
    for material in materials:
        root = get_root_material(material)
        if root:
            root_materials.add(root.get_path_name())


    print('root material count:', len(root_materials))
    
    for root_material in root_materials:
        print(root_material)

    return len(root_materials)

if __name__ == '__main__':
    
    asset_list = []
    asset_list.extend(unreal_utility.ListAssets('/Game/Buildings', 'SkeletalMesh'))
    asset_list.extend(unreal_utility.ListAssets('/Game/Models', 'SkeletalMesh'))
    
    print('asset count:', len(asset_list))

    asset_list = unreal_utility.CheckAssetUsed(asset_list)

    print('used asset count:', len(asset_list))

    materials = []

    def do_collect(asset_data):
        materials.extend(collect_material(asset_data))
        return asset_data.package_name

    unreal_utility.SlowTask(asset_list, do_collect, 'Collect Materials')

    materials = list(set(materials))
    
    print('material count:', len(materials))

    count = 0
    for material in materials:
        if CheckMaterialShouldSwitchOff(material):
            count += 1
            print(material.get_path_name())


    print('invalid material count:', count)
