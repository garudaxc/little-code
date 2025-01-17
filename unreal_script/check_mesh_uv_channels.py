import unreal
import os, sys


current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)

import perforce_tool

root_asset_name = unreal.Name('/Game/Blueprints/ResRefManager/DT_AssetPathMap')
output_file = 'd:/invalid_uv_channels.txt'
num_uv_limit = 1

def IsRootAsset(asset_name):
    return asset_name == root_asset_name

def IsReferenceByRoot(asset_registry, depend_options, asset_name : str, dep_path : list = []):
    depends = asset_registry.get_referencers(asset_name, depend_options)

    dep_path.append(asset_name)

    for dep in depends:
        if dep in dep_path: continue

        if IsRootAsset(dep):
            return True 
        elif IsReferenceByRoot(asset_registry, depend_options, dep, dep_path):
            return True
    
    dep_path.pop()
        
    return False


def ListAssets(asset_dir : str, type_name):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_datas = asset_registry.get_assets_by_path(asset_dir, True)

    asset_list = []
    for asset_data in asset_datas:
        type_match = asset_data.asset_class in type_name if isinstance(type_name, list) else asset_data.asset_class == type_name
        if asset_data.is_valid() and type_match:
            asset_list.append(asset_data)
            # print(asset_data.object_path)

    return asset_list



def CheckRedundantUVChannels(asset_data : unreal.AssetData, allow_lightmap_uv: bool = False):
    asset = asset_data.get_asset()
    
    # asset = unreal.EditorAssetLibrary.load_asset(asset_data.AssetName)
    if isinstance(asset, unreal.StaticMesh):
        
        if not allow_lightmap_uv:
            light_map_channel = asset.get_editor_property('light_map_coordinate_index')
            if light_map_channel > 0:
                return (False, 0)

        # if asset.get_editor_property('allow_cpu_access') :
        #     print(f'{asset_data.package_name} allow cpu access')

        num_channels = unreal.EditorStaticMeshLibrary.get_num_uv_channels(asset, 0)
        if num_channels > num_uv_limit:
            return (False, num_channels)
        
    elif isinstance(asset, unreal.SkeletalMesh):
        num_channels = unreal.EditorSkeletalMeshLibrary.get_num_uv_channels(asset, 0)
        if num_channels > num_uv_limit:
            return (False, num_channels)

    
    return (True, 0)



def RemoveExtraUV(asset_data : unreal.AssetData, remove_lightmap_uv : bool):
    asset = asset_data.get_asset()
    
    num_removed = 0
    if isinstance(asset, unreal.StaticMesh):

        if remove_lightmap_uv:

            light_map_channel = asset.get_editor_property('light_map_coordinate_index')
            if light_map_channel > 0:
                # print(f'{asset_data.package_name} light map coordinate index > 0')

                result = unreal.EditorStaticMeshLibrary.set_generate_lightmap_uv(asset, False)
                if result: num_removed += 1
                print(f'set_generate_lightmap_uvs {result}')

        num_lods = unreal.EditorStaticMeshLibrary.get_lod_count(asset)

        result = True
        for lod_index in range(num_lods):
            num_channels = unreal.EditorStaticMeshLibrary.get_num_uv_channels(asset, lod_index)

            for channel in range(num_channels - 1, 0, -1):

                result = unreal.EditorStaticMeshLibrary.remove_uv_channel(asset, lod_index, channel) and result                
                if result: num_removed += 1
                if not result:
                    print(f'remove uv channels failed {asset_data.package_name}')

        print(f'remove {asset_data.package_name} {num_removed} uv channels')
        return result
    
    else:
        print(asset)
        print(f'not support {asset_data.package_name}')
    
    return False




def CheckMeshUV():
        
    asset_list = []
    asset_list.extend(ListAssets('/Game/Buildings', ['StaticMesh', 'SkeletalMesh']))
    asset_list.extend(ListAssets('/Game/VFX', ['StaticMesh', 'SkeletalMesh']))
    asset_list.extend(ListAssets('/Game/Models', ['StaticMesh', 'SkeletalMesh']))
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    depend_options = unreal.AssetRegistryDependencyOptions(True, True, False, False, False)

    print(f'asset count {len(asset_list)}')

    with unreal.ScopedSlowTask(len(asset_list), 'Check Mesh UV Channels') as slow_task:
        slow_task.make_dialog(True)

        used_count = 0    
        invalid_asset_list = []
        for asset_data in asset_list:
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_data.package_name)

            asset_name = asset_data.package_name
            #资源需要被实际引用
            if IsReferenceByRoot(asset_registry, depend_options, asset_name):
                used_count += 1

                valid, num_channels = CheckRedundantUVChannels(asset_data)                
                if not valid:
                    invalid_asset_list.append((asset_data, num_channels))
                    
    print(f'used asset count {used_count} invalid count {len(invalid_asset_list)}')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('静态模型\n')
        for asset_data, num_channels in invalid_asset_list:
            if asset_data.asset_class == 'StaticMesh':
                f.write(f'{asset_data.package_name}\n')
        f.write('\n')

        f.write('骨骼模型\n')
        for asset_data, num_channels in invalid_asset_list:
            if asset_data.asset_class == 'SkeletalMesh':
                f.write(f'{asset_data.package_name}\n')

        # for asset in invalid_asset_list:
        #     if not CheckMeshUVChannels(asset):
        #         print(f'{asset.package_name} has more than 2 uv channels')




def BatchRemoveExtraUV(asset_list : list, only_check):
    p4 = perforce_tool.P4Wrapper()
    
    # check valid
    # 
    all_valid = True
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    for asset_name in asset_list:
        asset_data = asset_registry.get_asset_by_object_path(asset_name)
        if not (asset_data and asset_data.is_valid()):
            print(f'{asset_name} is invalid')
            all_valid = False

        if (asset_data.asset_class != 'StaticMesh'): # and (asset_data.asset_class != 'SkeletalMesh'):
            print(f'{asset_name} is not mesh')
            all_valid = False

        file_name = unreal.EditorAssetLibrary.package_name_to_file_name(asset_data.package_name)
        if file_name == '' or not os.path.exists(file_name):
            print(f'{asset_data.package_name} not exist on disk')
            all_valid = False

        if p4.IsLocalModified(file_name):
            print(f'{asset_data.package_name} is modified')
            all_valid = False

        if not p4.IsSynced(file_name):
            print(f'{asset_data.package_name} is not synced')
            all_valid = False

        pass_uv_check, _ = CheckRedundantUVChannels(asset_data)
        if pass_uv_check:
            print(f'{asset_data.package_name} has no redundant uv channels')
            all_valid = False


    if not all_valid:
        print('invalid asset list, please fix before retry')
        return
    
    # do do remove uv channels
    if not only_check:
        print("check out files")        
        for asset_name in asset_list:
            asset_data = asset_registry.get_asset_by_object_path(asset_name)
            file_name = unreal.EditorAssetLibrary.package_name_to_file_name(asset_data.package_name)
            if not p4.Checkout(file_name):
                print(f'checkout {asset_data.package_name} failed')
                break

        print("remove uv channels")
        for asset_name in asset_list:            
            asset_data = asset_registry.get_asset_by_object_path(asset_name)
            RemoveExtraUV(asset_data, True)

        print("done!")
    
        # if not CheckMeshUVChannels(asset_data):
        #     print(f'{asset_data.package_name} has more than {num_uv_limit} uv channels')


str_asset_list = '''
/Game/Buildings/K01/K01_B/K01_SmallBuiding_FYT_01/Meshes/K01_SmallBuidingFYT_posui01
/Game/Buildings/K01/K01_B/K01_SmallBuiding_FYT_01/Meshes/K01_SmallBuidingFYT_posui02
/Game/Buildings/K01/K01_B/K01_SmallBuiding_FYT_01/Meshes/K01_SmallBuidingFYT_posui03
/Game/Buildings/K01/K01_D/K01_Decal_Land_01
/Game/Buildings/K01/K01_F/K01_Cliff_DesertCliff_01
/Game/Buildings/K01/K01_F/K01_Cliff_DesertCliff_02
/Game/Buildings/K01/K01_F/K01_Cliff_DesertCliff_03
/Game/Buildings/K01/K01_F/K01_Tree_Oasis_11
/Game/Buildings/K01/K01_M/K01_Buildings_Floor_01
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_01
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_02
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_03
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_04
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_05
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_06
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_07
/Game/Buildings/K01/K01_M/K01_Buildings_TurenBC_08
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_01
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_02
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_03
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_04
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_05
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_06
/Game/Buildings/K01/K01_S/K01_SmallRock_Desert_07
/Game/Buildings/K02/K02_M/K02_Buildings_DuelField_020
/Game/Buildings/K02/K02_M/K02_Buildings_Pendant_05
/Game/Buildings/K02/K02_M/K02_Buildings_Pendant_06
/Game/Buildings/K02/K02_M/K02_Buildings_Pendant_07
/Game/Buildings/K02/K02_M/K02_Buildings_Pendant_09
/Game/Buildings/K02/K02_M/K02_Buildings_Pendant_13
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_01
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_02
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_03
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_04
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_05
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_06
/Game/Buildings/K02/K02_S/K02_SmallRock_jungle_07
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_01
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_02
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_03
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_04
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_05
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_06
/Game/Buildings/K02/K02_S/K02_SmallRock_snowfield_07
/Game/Buildings/K04/K04_M/K04_Buildings_ClimbingTower_01
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins01
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins02
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins03
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins04
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins05
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins06
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins07
/Game/Buildings/Meshes/K01/K01_B/K01_Ruins/K01_ruins08
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFCehassis01/K01_SmallBuilding_DFCehassis01/Meshes/K01_SmallBuilding_DFCehassis01_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFCehassis01/K01_SmallBuilding_DFCehassis02/Meshes/K01_SmallBuilding_DFCehassis02_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFCLLauncher_01/K01_SmallBuilding_DFCLLauncher_01_Down/Meshes/K01_SmallBuilding_DFCLLauncher_01_Down_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFCLLauncher_01/K01_SmallBuilding_DFCLLauncher_01_Up/Meshes/K01_SmallBuilding_DFCLLauncher_01_Up_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_Smallbuilding_DFEALauncher_01/Meshes/K01_Smallbuilding_DFEALauncher_01_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFPGLauncher_01/K01_SmallBuilding_DFPGLauncher_01_Down/Meshes/K01_SmallBuilding_DFPGLauncher_01_Down_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFPGLauncher_01/K01_SmallBuilding_DFPGLauncher_01_Up/Meshes/K01_SmallBuilding_DFPGLauncher_01_Up_Instanced
/Game/Buildings/Meshes/K01/K01_B/K01_SmallBuilding_DFSDLauncher_01/Meshes/K01_SmallBuilding_DFSDLauncher_01_Instanced
/Game/Buildings/Meshes/K01/K01_C/K01_Bridge_RainBow_01/K01_Bridge_RainBow_01
/Game/Buildings/Meshes/K01/K01_C/K01_Bridge_RainBow_01/K01_Bridge_RainBow_02
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_01
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_02
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_03
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_04
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_05
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_06
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_07
/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC/K01_Buildings_TurenBC_08
/Game/Buildings/Meshes/K01/K01_F/K01_Tree_AlienTree_03_02
/Game/Buildings/Meshes/K01/K01_F/K01_Tree_AlienTree_03_03
/Game/Buildings/Meshes/K01/K01_F/K01_Tree_AlienTree_03_04
/Game/Buildings/Meshes/K01/K01_F/K01_Tree_AlienTree_03_06
/Game/Buildings/Meshes/K01/K01_S/K01_Rock_Square/K01_Rock_Ruby_01
/Game/Buildings/Meshes/K01/K01_S/K01_Rock_Square/K01_Rock_Ruby_02
/Game/Buildings/Meshes/K01/K01_S/K01_Rock_Square/K01_Rock_Ruby_03
/Game/Buildings/Meshes/K02/K02_B/K02_SmallBuilding_RDLauncherNew_01/Meshes/K02_SmallBuilding_RDLauncherNew_01_Down_Instanced
/Game/Buildings/Meshes/K02/K02_B/K02_SmallBuilding_RDLauncherNew_01/Meshes/K02_SmallBuilding_RDLauncherNew_01_Instanced
/Game/Buildings/Meshes/K02/K02_B/K02_SmallBuilding_RDLauncherNew_02/Meshes/K02_SmallBuilding_RDLauncherNew_02_Instanced
/Game/Buildings/Meshes/K02/K02_B/K02_SuperBuilding_RainbowBridge_01/K02_SuperBuilding_RainbowBridge_01
/Game/Buildings/Meshes/K02/K02_B/K02_SuperBuilding_RainbowBridge_01/K02_SuperBuilding_RainbowBridgeCF_01/Meshes/K02_SuperBuilding_RainbowBridgeCF_01_Instanced
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_jijia01
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_jijia02
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_jijia03
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_renlei01
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_renlei02
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_renlei03
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_renlei04
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_tuling01
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_tuling02
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_tuling03
/Game/Buildings/Meshes/K02/K02_D/K02_Caiji_01/K02_caiji_tuling04
/Game/Buildings/Meshes/K02/K02_D/K02_Decal_Bacrystal_01/K02_Decal_Bacrystal_01
/Game/Buildings/Meshes/K02/K02_D/K02_Decal_Bacrystal_01/K02_Object_Bacrystal_01
/Game/Buildings/Meshes/K02/K02_D/K02_Decal_Bacrystal_01/K02_Object_Bacrystal_02
/Game/Buildings/Meshes/K02/K02_D/K02_Decal_Bacrystal_01/K02_Object_Bacrystal_03
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_B-SafeZone_ExteriorWall_01
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_B-SafeZone_ExteriorWall_02
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_B-SafeZone_ExteriorWall_03
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_B-SafeZone_ExteriorWall_04
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_B-SafeZone_ExteriorWall_05
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_B-SafeZone_ExteriorWall_06
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_Buildings_BLA_01
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_Buildings_BLA_04
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_Buildings_BLA_11
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_Airdrome_02
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_MCenter_02
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_MCenter_04
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_MCenter_06
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_MCenter_07
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_MCenter_10
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_MaxBuilding_MCenter_11
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_SafeZone_BuildRuins_01
/Game/Buildings/Meshes/K02/K02_M/SafeZone/K02_SafeZone_GiantGate_02
/Game/Buildings/Meshes/K02/K02_MMap/MMap_BossArea
/Game/Buildings/Meshes/K02/K02_MMap/MMap_bridge2
/Game/Buildings/Meshes/K02/K02_MMap/MMap_IncubationCentre02
/Game/Buildings/Meshes/K02/K02_MMap/MMap_slope
'''

def TestRemoveExtraUV(only_check = True):
    asset_list = [s.strip() for s in str_asset_list.splitlines()]    
    asset_list.remove("")

    # transform package name to asset name
    asset_list = [f"{s}.{s.split('/')[-1]}" for s in asset_list]
    BatchRemoveExtraUV(asset_list, only_check)


def TestRemoveSkeletalMeshUV(asset):
    assert asset.asset_class == 'SkeletalMesh'

    asset = asset.get_asset()
    num_lods = unreal.EditorSkeletalMeshLibrary.get_lod_count(asset)

    num_uv = unreal.EditorSkeletalMeshLibrary.get_num_uv_channels(asset, 0)

    print(f"num uv channels {num_uv}")

    if num_uv > 1:
        Result = unreal.EditorSkeletalMeshLibrary.remove_uv_channel(asset, 0, num_uv - 1)
        print(f"remove uv channels {Result}")


def Test():
    mesh = '/Game/VFX/Meshes/Cylinder/VFX_Mesh_Cylinder_0813.VFX_Mesh_Cylinder_0813'

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_data = asset_registry.get_asset_by_object_path(mesh)

    print(asset_data.package_name)
    print(asset_data.package_path)

    file_name = unreal.EditorAssetLibrary.package_name_to_file_name(asset_data.package_name)
    print(file_name)


def TestCheckout():
    package_list = [s.strip() for s in str_asset_list.splitlines()]    
    package_list.remove("")

    # transform package name to asset name
    asset_list = [f"{s}.{s.split('/')[-1]}" for s in package_list]

    p4 = perforce_tool.P4Wrapper()
    for asset_name in package_list[:3]:
        print('asset name ', asset_name)

        file_name = unreal.EditorAssetLibrary.package_name_to_file_name(asset_name)
        if p4.Checkout(file_name):
            print(f'checkout {asset_name} success')
        else:
            print(f'checkout {asset_name} failed')

if __name__ == '__main__':
    # TestRemoveExtraUV(False)

    asset = '/Game/Buildings/Meshes/K01/K01_C/K01_Buildings_TurenBC_03/Meshes/K01_Buildings_TurenBC_03.K01_Buildings_TurenBC_03'
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_data = asset_registry.get_asset_by_object_path(asset)
    TestRemoveSkeletalMeshUV(asset_data)
