import unreal
import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)
import unreal_utility
import perforce_tool


def BatchValidScreenSize(asset_list : list):
    '''
    screen size of lod 0 should be 1.0
    screen size of imposter should be 0.01
    '''

    invalid_list = []
    # asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    for asset_data in asset_list:
        asset_name = asset_data.package_name
        if asset_data.asset_class != 'StaticMesh':
            print(f'{asset_name} is not mesh')
            continue

        mesh = asset_data.get_asset()
        num_lods = mesh.get_num_lods()

        screen_sizes = unreal.EditorStaticMeshLibrary.get_lod_screen_sizes(mesh)
        for i, size in enumerate(screen_sizes):
            if (i == 0 and size != 1.0) or (i < num_lods - 1 and size == 0):
                invalid_list.append(asset_data)
                print(f'{asset_name} screen size {screen_sizes}')
                break

def package_path_to_asset_name(package_path):
    return f"{package_path}.{package_path.split('/')[-1]}"




def CheckoutFiles(asset_list : list, changelist_name : str = 'new changelist'):
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

        # if not p4.IsLocalModified(file_name):
        #     print(f'{asset_data.package_name} is not modified')
        #     all_valid = False

        if not p4.IsSynced(file_name):
            print(f'{asset_data.package_name} is not synced')
            all_valid = False

    if not all_valid:
        print('invalid asset list, please fix before retry')
        return

    print("check out files")
    file_list = []
    for asset_name in asset_list:
        asset_data = asset_registry.get_asset_by_object_path(asset_name)
        file_name = unreal.EditorAssetLibrary.package_name_to_file_name(asset_data.package_name)
        file_list.append(file_name)
        if not p4.Checkout(file_name):
            print(f'checkout {asset_data.package_name} failed')
            break

    result = p4.CreateChangeList(file_list, changelist_name)
    print('changelist', result)


if __name__ == '__main__':

    # asset_list = []
    # asset_list.extend(unreal_utility.ListAssets('/Game/Buildings', 'StaticMesh'))
    # asset_list.extend(unreal_utility.ListAssets('/Game/VFX', 'StaticMesh'))
    # asset_list.extend(unreal_utility.ListAssets('/Game/Models', 'StaticMesh'))
    # asset_list.extend(unreal_utility.ListAssets('/Game/Scence', 'StaticMesh'))
    # asset_list.extend(unreal_utility.ListAssets('/Game/World', 'StaticMesh'))

    # BatchValidScreenSize(asset_list)


    asset_list = [
        '/Game/Models/Vehicles/Skyload/Skyload01/Skyload01_Lower/Skyload01_Lower_Aircraft/Meshes/Skyload01_Lower_Aircraft_Instanced',
'/Game/Models/Vehicles/Thor/Thor01/Ther01_Lower/Ther01_Lower/Meshes/Thor01_Lower_Down_Instanced',
'/Game/Models/Vehicles/Thor/Thor01/Ther01_Lower/Ther01_Lower/Meshes/Thor01_Lower_Up_Instanced',
'/Game/Models/Vehicles/Thor/Thor01/Ther01_Lower/Thor01_Lower_Guns/Meshes/Thor01_Lower_Guns_Instanced',
'/Game/Models/Vehicles/Titan/Titan01/Titan01_Lower/Meshes/Titan01_Lower_Instanced'
    ]
    
    reduction_options = unreal.EditorScriptingMeshReductionOptions()
    editor_scripting_mesh_reduction_settings = unreal.EditorScriptingMeshReductionSettings()
    editor_scripting_mesh_reduction_settings.percent_triangles = 1.0
    editor_scripting_mesh_reduction_settings.screen_size = 1.0

    reduction_options.reduction_settings.append(editor_scripting_mesh_reduction_settings)

    asset_list = [package_path_to_asset_name(asset) for asset in asset_list]

    print('asset count:', len(asset_list))
    # CheckoutFiles(asset_list, 'fix screen size')
    

    for asset_name in asset_list:
        mesh = unreal.EditorAssetLibrary.load_asset(asset_name)
        print(asset_name)
        assert mesh

        unreal.EditorStaticMeshLibrary.set_lods_with_notification(mesh, reduction_options, True)
