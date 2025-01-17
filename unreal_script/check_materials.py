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


def get_material_property_override(material_instance):
    override = material_instance.get_editor_property('BasePropertyOverrides')

    property_names = ['bOverride_OpacityMaskClipValue', 'bOverride_BlendMode', 'bOverride_ShadingModel', 'bOverride_DitheredLODTransition', 'bOverride_CastDynamicShadowAsMasked', 'bOverride_TwoSided',
                      'bOverride_MobileSeparateTranslucency', 'TwoSided', 'DitheredLODTransition', 'bCastDynamicShadowAsMasked', 'bIsMobileSeparateTranslucencyEnabled', 'BlendMode',
                      'ShadingModel', 'OpacityMaskClipValue']
    
    property_override = {}
    for property_name in property_names:
        if property_name == 'BlendMode':
            property_override[property_name] = override.get_editor_property('BlendMode').value

        elif property_name == 'ShadingModel':
            property_override[property_name] = override.get_editor_property('ShadingModel').value
        
        else:        
            property_override[property_name] = override.get_editor_property(property_name)

    return property_override


def get_base_material(material_instance):

    base = material_instance
    while (base != None) and (not isinstance(base, unreal.Material)):
        base = base.parent

    return base


class MaterialCheckResult:
    parent_is_none = 1
    base_material_is_none = 2
    base_shading_model_not_match = 3

    def __init__(self, asset_data, type, *param):
        self.asset_data = asset_data
        self.type = type
        if type == MaterialCheckResult.base_shading_model_not_match:
            self.base_shading_model = param[0]
            self.override_shading_model = param[1]

    def __str__(self):
        if self.type == MaterialCheckResult.parent_is_none:
            return f'{self.asset_data.package_name} parent is None'
        elif self.type == MaterialCheckResult.base_material_is_none:
            return f'{self.asset_data.package_name} base material is None'
        elif self.type == MaterialCheckResult.base_shading_model_not_match:
            # return f'{self.asset_data.package_name} base shading model {self.base_shading_model} override shading model {self.override_shading_model}'
        
            return f'{self.asset_data.package_name}'
        

def check_material(asset_data : unreal.AssetData):
    '''
    检查材质实例是否使用了Override ShadingModel
    '''
    asset = asset_data.get_asset()
    if isinstance(asset, unreal.MaterialInstanceConstant):
        parent = asset.parent
        if parent == None:
            return MaterialCheckResult(asset_data, MaterialCheckResult.parent_is_none)

        override = get_material_property_override(asset)

        if override['bOverride_ShadingModel']:
            base_material = get_base_material(asset)
            if base_material == None:
                return MaterialCheckResult(asset_data, MaterialCheckResult.base_material_is_none)

            base_shading_model = base_material.get_editor_property('ShadingModel').value
            if base_shading_model != override['ShadingModel']:
                return MaterialCheckResult(asset_data, MaterialCheckResult.base_shading_model_not_match, base_shading_model, override['ShadingModel'])
        
    return None





if __name__ == "__main__":

    # test_asset = '/Game/TestAsset/xuchao/shadow/M_unlit_shadow_Inst.M_unlit_shadow_Inst'
    # asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    # asset_data = asset_registry.get_asset_by_object_path(test_asset)

    # if asset_data:
    #     result = check_material(asset_data)
    #     print(result)


    check_asset = '''
/Game/Buildings/K01/K01_B/Common/Materials/MI_K01_Building_LG
/Game/Buildings/K01/K01_F/MI_K01_Decal_Bridging_01
/Game/Buildings/K01/K01_F/MI_K01_Decal_Bridging_01_B
/Game/Buildings/K01/K01_F/MI_K01_Decal_Bridging_02
/Game/Buildings/K01/K01_F/MI_K01_Decal_Bridging_03
/Game/Buildings/K01/K01_M/MI_K01_Decal_Floor_01
/Game/Buildings/K01/K01_M/MI_K01_Decal_Floor_02
/Game/Buildings/K02/K02_B/Common/Materials/MI_K02_CBuilding_Decal_01
/Game/Buildings/K02/K02_B/K02_Object_BacrystalB/Materials/MI_K02_Object_BacrystalB_02
/Game/Buildings/K02/K02_D/MI_K02_Decal_Land
/Game/Buildings/K02/K02_D/MI_K02_Decal_Vistas_03
/Game/Buildings/K02/K02_D/MI_K02_Object_Vistas_03
/Game/Buildings/K02/K02_F/MI_K02_Decal_VVS_01
/Game/Buildings/Materials/MaterialInsts/K01/K01_D/K01_Decal_Crater_01/M_Explosicum_Inst
/Game/Buildings/Materials/MaterialInsts/K01/K01_D/K01_Decal_Flower_01/MI_K01_Decal_Flower_01
/Game/Buildings/Materials/MaterialInsts/K01/K01_D/K01_muxing_gonglu01/MI_K01_muxing_gonglu03
/Game/Buildings/Materials/MaterialInsts/K01/K01_D/K01_muxing_gonglu01/MI_K01_muxing_gonglu04
/Game/Buildings/Materials/MaterialInsts/K02/K02_D/K02_Decal_Bacrystal_01/MI_K02_Decal_Bacrystal_01
/Game/Buildings/Materials/MaterialInsts/K02/K02_D/K02_Decal_Iridium_01/MI_K02_Decal_Iridium_01
/Game/Buildings/Materials/MaterialInsts/K02/K02_D/K02_Decal_Metal_01/K02_Decal_Metal_01
/Game/Buildings/Materials/MaterialInsts/K02/K02_F/K02_Vegetation_Iceberg/MI_K02_Decal_IVS_01
/Game/Buildings/Materials/MaterialInsts/K02/K02_F/K02_Vegetation_Oasis/MI_K02_Decal_OVSB_01
/Game/Buildings/Materials/MaterialInsts/K02/K02_F/K02_Vegetation_Snowfield/MI_K02_Decal_SVSA_01
/Game/Buildings/Materials/MaterialInsts/K02/K02_F/K02_Vegetation_Volcano/MI_K02_Decal_VVS_01
/Game/VFX/Material/MateriallnstsBattle/VFX_MI_Battle_Base_Hero_0500
/Game/VFX/Material/MateriallnstsShow/VFX_MI_BasicX_0301
/Game/VFX/Material/MateriallnstsShow/VFX_MI_BasicX_0302
/Game/VFX/Material/MateriallnstsShow/VFX_MI_BasicX_0303
/Game/VFX/Material/MateriallnstsShow/VFX_MI_BasicX_0304
/Game/Models/Armies/MonsterCorpse/Materials/M_Warpchaser
/Game/Models/Armies/XB_Warpchaser_New/Materials/M_Warpchaser
/Game/Models/Armies/XB_Warpchaser_New/Materials/M_Warpchaser01
/Game/Models/Armies/XB_Warpchaser_New/Materials/M_Warpchaser02
/Game/Models/Armies/XB_Warpchaser_New/Materials/M_Warpchaser03
/Game/Models/Armies/XB_Warpchaser_New/Materials/M_Warpchaser04
/Game/Models/Armies/XB_Warpchaser_New/Materials/M_Warpchaser_2
/Game/Models/NPC/SH_Bagration_Quanxi/Materials/M_SH_Bagration_Quanxi
'''


    asset_list = []
    asset_list.extend(ListAssets('/Game/Buildings', ['MaterialInstanceConstant']))
    asset_list.extend(ListAssets('/Game/VFX', ['MaterialInstanceConstant']))
    asset_list.extend(ListAssets('/Game/Models', ['MaterialInstanceConstant']))
    asset_list.extend(ListAssets('/Game/Scence', ['MaterialInstanceConstant']))
    asset_list.extend(ListAssets('/Game/UI', ['MaterialInstanceConstant']))
    asset_list.extend(ListAssets('/Game/World', ['MaterialInstanceConstant']))

    print(f'asset count {len(asset_list)}')

    results = []

    with unreal.ScopedSlowTask(len(asset_list), 'Check Mesh UV Channels') as slow_task:
        slow_task.make_dialog(True)

        for asset_data in asset_list:
            if slow_task.should_cancel(): break
            slow_task.enter_progress_frame(1, asset_data.package_name)

            result = check_material(asset_data)
            if result:
                results.append(result)

    print(f'invalid material count {len(results)}')
    for result in results:
        print(str(result))