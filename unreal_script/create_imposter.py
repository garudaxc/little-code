import unreal
import os
import sys
import importlib


current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)

if 'perforce_tool' in sys.modules:
    print('relod module')
    importlib.reload(sys.modules['perforce_tool'])

import perforce_tool


lod_mesh_path = '/Game/TestAsset/xuchao/imposter/simple_plane.simple_plane'
lod_mesh = None

setting_asset = '/Game/TestAsset/xuchao/imposter/ImposterMobileCaptureSettings.ImposterMobileCaptureSettings'

asset_path = '/Game/Buildings/K02/K02_F/K02_Tree_Snowfield_07.K02_Tree_Snowfield_07'

def create_imposter(asset_path, settings, out_dir):
    
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_data = asset_registry.get_asset_by_object_path(asset_path)

    assert asset_data
    mesh = asset_data.get_asset()

    imposter_manager = unreal.ImposterManagerActor
    imposter_manager.generate_imposter_for_mesh(mesh, settings, out_dir)



def TestBakeImposter():

    bake_setting = unreal.EditorAssetLibrary.load_asset(setting_asset)
    assert bake_setting
    print(type(bake_setting))

    out_dir = '/Game/TestAsset/xuchao/imposter/Out/'

    create_imposter(asset_path, bake_setting, out_dir)

def GetAssetPathDir(path : str):
    index = path.rfind('/')

    assert index != -1
    return path[:index + 1]

def GetAssetName(path : str):
    index = path.rfind('.')
    if index == -1:
        index = path.rfind('/')

    assert index != -1

    return path[index+1:]


def CheckOrAddLodToMesh(mesh, only_check : bool, lod_mesh):
    num_lods = mesh.get_num_lods()
    last_lod = num_lods - 1
    num_vertex = unreal.EditorStaticMeshLibrary.get_number_verts(mesh, last_lod)

    if only_check or (not lod_mesh):
        if num_lods == 1:
            return False
        
        if num_vertex != 4:
            return False
        
    # use or create lod, no more than 3 lods
    if num_vertex != 4:
        if num_lods > 2:
            print(f'asset {asset_path} has {num_lods} lods and {num_vertex} vertex')
            print('最后一级lod应为imposter')
            return False
        
        else:
            # add lod to mesh
            result = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(mesh, num_lods, lod_mesh, 0, False)
            return result

    return True




def CreateFoliageImposterLod(asset_path, add_lod_to_mesh = False, lod_mesh = None):
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    asset_data = asset_registry.get_asset_by_object_path(asset_path)

    if not asset_data:
        print(f'asset {asset_path} not found')
        return False
    
    if asset_data.asset_class != 'StaticMesh':
        print(f'asset {asset_path} is not a static mesh')
        return False
    
    mesh = asset_data.get_asset()
    assert mesh

    if not CheckOrAddLodToMesh(mesh, not add_lod_to_mesh, lod_mesh):
        print(f'asset {asset_path} check or add lod failed')
        return False

    asset_dir = GetAssetPathDir(asset_path)
    asset_name = GetAssetName(asset_path)
    out_dir = os.path.join(asset_dir, 'Imposter')
    out_name = f'{asset_name}_Imposter'
    
    bake_setting = unreal.EditorAssetLibrary.load_asset(setting_asset)
    assert bake_setting

    imposter_manager = unreal.ImposterManagerActor
    result = imposter_manager.generate_imposter_for_mesh(mesh, bake_setting, out_dir, out_name)
    if not result:
        print(f'create imposter for {asset_path} failed')
        return False
    
    lod_material_path = f'{out_dir}/MI_{out_name}.MI_{out_name}'
    lod_material = unreal.EditorAssetLibrary.load_asset(lod_material_path)
    assert lod_material
    
    num_lods = mesh.get_num_lods()
    last_lod = num_lods - 1
    material_slot = unreal.EditorStaticMeshLibrary.get_lod_material_slot(mesh, last_lod, 0)

    # set material slot name    
    materials = mesh.static_materials
    mesh_material = materials[material_slot]
    mesh_material.material_slot_name = unreal.Name('Imposter')
    materials[material_slot] = mesh_material
    mesh.static_materials = materials

    mesh.set_material(material_slot, lod_material)
    result = unreal.EditorStaticMeshLibrary.set_lod_screen_size(mesh, last_lod, 0.01)

    return result





def CheckoutFiles(asset_list : list):
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

    result = p4.CreateChangeList(file_list, 'imposter changelist')
    print('changelist', result)

    print("done!")



def GetAssetList():
        
    asset_to_process = '''
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_10
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_11
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_01
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_02
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_03
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_04
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_05
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_06
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_07
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_08
    /Game/Buildings/K02/K02_F/K02_Tree_Oasis_09
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_11
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_01
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_02
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_03
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_04
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_05
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_06
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_07
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_08
    /Game/Buildings/K02/K02_F/K02_Tree_Snowfield_09
    /Game/Buildings/K01/K01_F/K01_Tree_Oasis_11
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_10
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_12
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_17
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_18
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_19
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_010
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_011
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_012
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_013
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_015
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_016
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_017
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_018
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_07
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_08
    /Game/Buildings/K01/K01_F/K01_Tree_Pine_09
    /Game/Buildings/K01/K01_F/T_K01_Tree_Plant_4
    /Game/Buildings/K01/K01_F/T_K01_Tree_Plant_03
    /Game/Buildings/K02/K02_F/M_K02_SpaceBush_01
    /Game/Buildings/K02/K02_F/M_K02_SpaceBush_02
    /Game/Buildings/K02/K02_F/M_K02_SpaceBush_03
    /Game/Buildings/K02/K02_F/M_K02_SpaceBush_04
    /Game/Buildings/K02/K02_F/M_K02_SpaceTree_01
'''
    
# '/Game/Buildings/K02/K02_F/M_K02_SpaceTree_01.M_K02_SpaceTree_01'

    asset_list = [s.strip() for s in asset_to_process.splitlines()]    
    asset_list.remove("")

    # transform package name to asset name
    asset_list = [f"{s}.{s.split('/')[-1]}" for s in asset_list]

    return asset_list



def StatMeshLods():
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    lods_count = [0] * 3

    for asset_path in GetAssetList():
        mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
        print(asset_path)
        assert mesh
        #and mesh.static_class() == unreal.StaticMesh
        num_lods = mesh.get_num_lods()

        lods_count[num_lods - 1] += 1

    print(f'lods count {lods_count}')


def TestMakeDensityScale():
    asset = '/Game/Buildings/K02/K02_F/K02_Tree_Oasis_04.K02_Tree_Oasis_04'
    mesh = unreal.EditorAssetLibrary.load_asset(asset)
    
    print(asset)
    assert mesh

    asset_data = mesh.get_editor_property('AssetUserData')
    if len(asset_data) > 0:
        data = asset_data[0]
        if not data:
            print('density data is null')

    asset_data = unreal.Array(unreal.AssetUserData)
    data = unreal.InstanceDensityScalingEnabled()


    # print(data)
    # [print(i) for i in dir(data)]
    # scale = data.get_editor_property('Scale')
    # print(scale)
    # r = data.get_editor_property('Range')
    # print(r)
    # up = r.get_editor_property('UpperBound')
    # print(up)
    # up.set_editor_property('Value', 0.5)
    # r.set_editor_property('UpperBound', up)
    # data.set_editor_property('Range', r)
    
    asset_data.append(data)
    mesh.set_editor_property('AssetUserData', asset_data)


    # print(data)
    # print(data.Range)



def BatchMakeDensityScale():

    asset_path = GetAssetList()
    with unreal.ScopedSlowTask(len(asset_path), 'checking') as slow_task:
        slow_task.make_dialog(True)
    
        for asset_path in asset_path:
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_path)

            mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
            
            asset_data = mesh.get_editor_property('AssetUserData')
            if len(asset_data) > 0:
                data = asset_data[0]
                if not data:
                    print('density data is null')
                else:
                    data.static_class() == unreal.InstanceDensityScalingEnabled
                    print("already has density data")
                    continue

            user_data = unreal.Array(unreal.AssetUserData)
            data = unreal.InstanceDensityScalingEnabled(mesh)

            user_data.append(data)
            mesh.set_editor_property('AssetUserData', user_data)


    print('done')




def BatchCreateImposter():
    import time

    lod_mesh = unreal.EditorAssetLibrary.load_asset(lod_mesh_path)
    assert lod_mesh

    succeeded = True

    asset_path = GetAssetList()
    with unreal.ScopedSlowTask(len(asset_path), 'checking') as slow_task:
        slow_task.make_dialog(True)
    
        for asset_path in asset_path:
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_path)

            if asset_path.find('K01') == -1:
                continue
            
            if not CreateFoliageImposterLod(asset_path, True, lod_mesh):
                print(f'create imposter for {asset_path} failed')
                succeeded = False
                break

            time.sleep(1.5)

    if succeeded:
        print('all imposter created')




def TestCreateLod(asset_path):
    mesh = unreal.EditorAssetLibrary.load_asset(asset_path)
    assert mesh

    num_lods = mesh.get_num_lods()
    
    # if num_lods > 1:
    #     return True    

    redution_option = unreal.EditorScriptingMeshReductionOptions()
    redution_option.auto_compute_lod_screen_size = False
    
    redution_setting = unreal.EditorScriptingMeshReductionSettings()
    redution_setting.percent_triangles = 1.0
    redution_setting.screen_size = 1.0
    redution_option.reduction_settings.append(redution_setting)
    redution_setting = unreal.EditorScriptingMeshReductionSettings()
    redution_setting.percent_triangles = 0.5
    redution_setting.screen_size = 0.05
    redution_option.reduction_settings.append(redution_setting)


    result = unreal.EditorStaticMeshLibrary.set_lods(mesh, redution_option)
    print(f'set lod result {result}')



def FindMeshWithOnlyImposter():
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    for asset_name in GetAssetList():
        asset_data = asset_registry.get_asset_by_object_path(asset_name)
        if not (asset_data and asset_data.is_valid()):
            continue

        if asset_data.asset_class != 'StaticMesh':
            continue

        mesh = asset_data.get_asset()
        if mesh.get_num_lods() == 3:
            print(f'{asset_name} has 2 lod')



if __name__ == "__main__":

    if True:
        FindMeshWithOnlyImposter()

        # test_asset = '/Game/Buildings/K02/K02_F/K02_Tree_Oasis_10.K02_Tree_Oasis_10'
        # TestCreateLod(test_asset)

        # CheckoutFiles(GetAssetList())

        # BatchMakeDensityScale()
        # TestMakeDensityScale()

        # BatchCreateImposter()

        # StatMeshLods()
    
    else:
        asset_path = '/Game/Buildings/K02/K02_F/M_K02_SpaceTree_01.M_K02_SpaceTree_01'

        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        lod_mesh = unreal.EditorAssetLibrary.load_asset(lod_mesh_path)
        assert lod_mesh


        CreateFoliageImposterLod(asset_path, True, lod_mesh)

    if False:


        asset_data = asset_registry.get_asset_by_object_path(asset_path)

        assert asset_data
        mesh = asset_data.get_asset()

        num_lods = mesh.get_num_lods()

        last_lod = num_lods - 1
        num_sections = mesh.get_num_sections(last_lod)

        num_vertex = unreal.EditorStaticMeshLibrary.get_number_verts(mesh, last_lod)

        print(f'lods {num_lods} sections {num_sections} vertex {num_vertex}')

        # if num_lods > 1 and num_vertex == 4:
        if num_lods == 1 or num_vertex != 4:
            result = unreal.EditorStaticMeshLibrary.set_lod_from_static_mesh(mesh, num_lods, lod_mesh, 0, False)
            print(f'result {result}')




    # sel = unreal.EditorUtilityLibrary.get_selection_set()
    # for obj in sel:
    #     print(obj)

    # actor = sel[0]

    # [print(a) for a in dir(unreal.ImposterManagerActor)]

    # print(unreal.ImposterManagerActor.generate_imposter_for_mesh)

    # iter = unreal.ActorIterator()
    # for actor in iter:
    #     print(actor)

    
    
    # asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    # asset_data = asset_registry.get_asset_by_object_path(asset_path)

    # assert asset_data

    # create_imposter(asset_data)

    pass