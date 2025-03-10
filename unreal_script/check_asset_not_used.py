import unreal
import os
import sys



root_asset_name = unreal.Name('/Game/Blueprints/ResRefManager/DT_AssetPathMap')

def IsRootAsset(asset_name):
    return asset_name == root_asset_name

def IsReferenceByRoot(asset_registry, depend_options, asset_name : str, valid_set, dep_path : list = []):
    depends = asset_registry.get_referencers(asset_name, depend_options)

    dep_path.append(asset_name)

    for dep in depends:
        # print(f'dep {len(dep_path)} : {dep}')

        if dep in dep_path: continue

        if dep in valid_set:
            return True

        if IsRootAsset(dep):
            return True 
        elif IsReferenceByRoot(asset_registry, depend_options, dep, valid_set, dep_path):
            for mid_deps in dep_path:
                valid_set.add(mid_deps)
            return True
    
    dep_path.pop()
        
    return False


def ListAssets(asset_dir : str, type_name):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_datas = asset_registry.get_assets_by_path(asset_dir, True)

    asset_list = []
    for asset_data in asset_datas:
        type_match = True
        if type_name != None:
            type_match = asset_data.asset_class in type_name if isinstance(type_name, list) else asset_data.asset_class == type_name

        if asset_data.is_valid() and type_match:
            asset_list.append(asset_data)

    return asset_list


def CheckAssetNotUsed(asset_list):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    depend_options = unreal.AssetRegistryDependencyOptions(True, True, False, False, False)

    not_used_assets = []
    valid_assets = set()
        
    with unreal.ScopedSlowTask(len(asset_list), 'Check Asset Not Used') as slow_task:
        slow_task.make_dialog(True)

        for asset_data in asset_list:
            asset_name = asset_data.package_name
            # print('check asset:', asset_name)
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_name)
            
            if IsReferenceByRoot(asset_registry, depend_options, asset_name, valid_assets, list()):
                valid_assets.add(asset_name)
            else:
                not_used_assets.append(asset_name)

    print('Not used assets:', len(not_used_assets))
    # for asset_name in not_used_assets:
    #     print(asset_name)

    #save to file
    file_path = os.path.join(os.path.dirname(__file__), 'not_used_assets.txt')
    with open(file_path, 'w') as f:
        for asset_name in not_used_assets:
            f.write(str(asset_name) + '\n')
    print('save to file:', file_path)


def CheckAssetUsed(asset_list):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    depend_options = unreal.AssetRegistryDependencyOptions(True, True, False, False, False)

    used_assets = []
    valid_assets = set()

    with unreal.ScopedSlowTask(len(asset_list), 'Check Asset Used') as slow_task:
        slow_task.make_dialog(True)

        for asset_data in asset_list:
            asset_name = asset_data.package_name
            # print('check asset:', asset_name)
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_name)

            if IsReferenceByRoot(asset_registry, depend_options, asset_name, valid_assets, list()):
                valid_assets.add(asset_name)
                used_assets.append(asset_name)

    print('used assets:', len(used_assets))
    #save to file
    file_path = os.path.join(os.path.dirname(__file__), 'used_assets.txt')
    with open(file_path, 'w') as f:
        for asset_name in used_assets:
            f.write(str(asset_name) + '\n')
    print('save to file:', file_path)

    # open file with shell
    os.system('start ' + file_path)


if __name__ == '__main__':

    asset_list = []
    # asset_list.extend(ListAssets('/Game/Buildings', None))
    # asset_list.extend(ListAssets('/Game/VFX', None))
    # asset_list.extend(ListAssets('/Game/Models', None))
    # asset_list.extend(ListAssets('/Game/Scence', None))
    # asset_list.extend(ListAssets('/Game/UI', None))
    # asset_list.extend(ListAssets('/Game/World', None))
    asset_list.extend(ListAssets('/Game/VFX/Textures/UI', None))
    CheckAssetNotUsed(asset_list)

    # asset_list = []
    # asset_list.extend(ListAssets('/Game/Buildings/Materials', None))
    # asset_list.extend(ListAssets('/Game/Buildings/Meshes', None))
    # asset_list.extend(ListAssets('/Game/Buildings/Textures', None))
    # CheckAssetUsed(asset_list)