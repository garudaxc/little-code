
import unreal
import sys, inspect
import os


def PackagePathToName(package_path):
    return f'{package_path}.{package_path.split("/")[-1]}'

def LoadTemplateTransform(template_bp_path):
    template_bp_path = PackagePathToName(template_bp_path)
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    asset_data = asset_registry.get_asset_by_object_path(template_bp_path)

    assert asset_data.asset_class == "Blueprint"

    bp_class = unreal.EditorAssetLibrary.load_blueprint_class(template_bp_path)
    bp_class_asset = unreal.EditorAssetLibrary.load_asset(template_bp_path)
    assert bp_class is not None

    comp_transforms = {}

    sub_objs = unreal.K6UtilityFunctionLibrary.get_objects_with_outer_object(bp_class)
    for sub_obj in sub_objs:
        if isinstance(sub_obj, unreal.ChildActorComponent):
            name = sub_obj.get_name()
            transform = sub_obj.get_relative_transform()
            comp_transforms[name] = transform

    return comp_transforms


def compare_transform(t1, t2):
    if t1.translation != t2.translation:
        return False

    if t1.rotation != t2.rotation:
        return False

    if t1.scale3d != t2.scale3d:
        return False

    return True


def ModifyMineComponentTransform(comp_transforms, target_bp_paths):

    for target_pbp in target_bp_paths:
        target_pbp = PackagePathToName(target_pbp)
        target_bp_asset = unreal.EditorAssetLibrary.load_asset(target_pbp)
        assert target_bp_asset is not None

        bp_class = unreal.EditorAssetLibrary.load_blueprint_class(target_pbp)
        num_actor_components = 0
        sub_objs = unreal.K6UtilityFunctionLibrary.get_objects_with_outer_object(bp_class)
        
        for sub_obj in sub_objs:
            if isinstance(sub_obj, unreal.ChildActorComponent):
                num_actor_components += 1
                if sub_obj.get_name().find('BP_K02_Object_BigOre_06_ex') != -1:
                    continue

                if not (sub_obj.get_name() in comp_transforms):
                    raise Exception(f'{sub_obj.get_name()} not found in {target_pbp}')
        
        different = False
        for sub_obj in sub_objs:
            if isinstance(sub_obj, unreal.ChildActorComponent):
                name = sub_obj.get_name()
                
                if not comp_transforms.get(name):
                    print(f'{name} not found in {target_pbp}')
                    continue
                old_transform = sub_obj.get_relative_transform()
                transfrom = comp_transforms[name]

                if not compare_transform(old_transform, transfrom):
                    different = True

        if not different:
            print(f'{target_pbp} transform is same')
            continue
        
        checkout_result = unreal.EditorAssetLibrary.checkout_asset(target_pbp)
        if not checkout_result:
            raise Exception(f'checkout {target_pbp} failed')
        
        for sub_obj in sub_objs:
            if isinstance(sub_obj, unreal.ChildActorComponent):
                name = sub_obj.get_name()

                if not comp_transforms.get(name):
                    print(f'{name} not found in {target_pbp}')
                    continue
                old_transform = sub_obj.get_relative_transform()
                transfrom = comp_transforms[name]

                sub_obj.set_relative_transform(transfrom, False, False)

        unreal.EditorAssetLibrary.save_loaded_asset(target_bp_asset, False)
            
    print('done')


if __name__ == '__main__':

    template_bp_path = '/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_1_1'
    target_bp_path = ['/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_1_1',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_1_2',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_1_3',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_1_4',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_1_2',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_1_3',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_1_4']

    ModifyMineComponentTransform(LoadTemplateTransform(template_bp_path), target_bp_path)

    
    template_bp_path = '/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_2_1'
    target_bp_path = ['/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_2_1',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_2_2',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_2_3',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_2_4',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_2_2',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_2_3',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_2_4']

    ModifyMineComponentTransform(LoadTemplateTransform(template_bp_path), target_bp_path)
    
    
    template_bp_path = '/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_3_1'
    target_bp_path = ['/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_3_1',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_3_2',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_3_3',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_3_4',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_3_2',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_3_3',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_3_4']

    ModifyMineComponentTransform(LoadTemplateTransform(template_bp_path), target_bp_path)

    
    template_bp_path = '/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_4_1'
    target_bp_path = ['/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_4_1',
'/Game/Editor/TemplateMine/guoduzhou/BP_Ore12Mine_4_2',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_4_2',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_4_02',
'/Game/Editor/TemplateMine/chushengzhou/BP_Ore20Mine_4_4']

    ModifyMineComponentTransform(LoadTemplateTransform(template_bp_path), target_bp_path)