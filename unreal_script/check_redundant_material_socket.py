import unreal
import os, sys


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



def check_redundant_material(asset_data : unreal.AssetData):

    asset = asset_data.get_asset()
    
    # asset = unreal.EditorAssetLibrary.load_asset(asset_data.AssetName)
    if isinstance(asset, unreal.StaticMesh):
        static_materials = asset.static_materials

        num_materials = len(static_materials)
        num_lods = asset.get_num_lods()
        total_sections = 0
        for lod_index in range(num_lods):
            num_sections = asset.get_num_sections(lod_index)
            total_sections += num_sections

        if num_materials > total_sections:
            return (num_materials, total_sections)

            # print(f'{asset_data.package_name} materials {num_materials} used {total_sections}')

    elif isinstance(asset, unreal.SkeletalMesh):
        num_materials = len(asset.materials)
        num_lods = unreal.EditorSkeletalMeshLibrary.get_lod_count(asset)
        total_sections = 0
        for lod_index in range(num_lods):
            num_sections = unreal.EditorSkeletalMeshLibrary.get_num_sections(asset, lod_index)
            total_sections += num_sections

        if num_materials > total_sections:
            return (num_materials, total_sections)
        
    return None



if __name__ == "__main__":
    # test_asset = '/Game/TestAsset/xuchao/LSZZ/Mesh/1331.1331'
    # test_asset = '/Game/TestAsset/xuchao/Animation/skin_box.skin_box'
    # asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    # asset_data = asset_registry.get_asset_by_object_path(test_asset)

    # if asset_data:
    #     result = check_redundant_material(asset_data)
    #     print(result)

    
    asset_list = []
    asset_list.extend(ListAssets('/Game/Buildings', ['StaticMesh', 'SkeletalMesh']))
    asset_list.extend(ListAssets('/Game/VFX', ['StaticMesh', 'SkeletalMesh']))
    asset_list.extend(ListAssets('/Game/Models', ['StaticMesh', 'SkeletalMesh']))    

    print(f'asset count {len(asset_list)}')

    results = []

    with unreal.ScopedSlowTask(len(asset_list), 'Check Mesh UV Channels') as slow_task:
        slow_task.make_dialog(True)

        for asset_data in asset_list:
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_data.package_name)

            result = check_redundant_material(asset_data)
            if result:
                results.append((asset_data, result))

    for asset_data, result in results:
        print(f'{asset_data.package_name} materials {result[0]} used {result[1]}')