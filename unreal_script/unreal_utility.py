import unreal
import os, sys

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)
import perforce_tool

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



def CheckAssetUsed(asset_list, slow_task = False):
    if asset_list == None or len(asset_list) == 0:
        print('asset list is empty')
        return
    
    if not isinstance(asset_list[0], unreal.AssetData):
        print('asset list type error')
        return

    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    depend_options = unreal.AssetRegistryDependencyOptions(True, True, False, False, False)

    used_assets = []
    valid_assets = set()

    def check(asset_name, asset_data):
        if IsReferenceByRoot(asset_registry, depend_options, asset_name, valid_assets, list()):
            valid_assets.add(asset_name)
            used_assets.append(asset_data)


    if slow_task:
        with unreal.ScopedSlowTask(len(asset_list), 'Check Asset Used') as slow_task:
            slow_task.make_dialog(True)

            for asset_data in asset_list:
                asset_name = asset_data.package_name
                # print('check asset:', asset_name)
                if slow_task.should_cancel(): break
                slow_task.enter_progress_frame(1, asset_name)

                check(asset_name, asset_data)
    else:
        for asset_data in asset_list:
            check(asset_data.package_name, asset_data)

    return used_assets


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


def package_path_to_asset_name(package_path):
    return f"{package_path}.{package_path.split('/')[-1]}"


def SlowTask(container, func, title = 'Slow Task'):
    with unreal.ScopedSlowTask(len(container), title) as slow_task:
        slow_task.make_dialog(True)

        for item in container:
            if slow_task.should_cancel(): break
            info = func(item)
            slow_task.enter_progress_frame(1, info)