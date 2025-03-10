import unreal
import os
import sys


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


def CheckTextureSize(asset_list):

    texGroup = unreal.TextureGroup.TEXTUREGROUP_PROJECT02

    for asset in asset_list:
        texture = asset.get_asset()
        # print(asset.package_name)
        # print(texture.lod_group.value, texture.lod_group.name)

        # # print(dir(texture.lod_group))
        # print(texture.blueprint_get_size_x())

        # print(f'{asset.package_name} {texture.width}x{texture.height}')

        if (texture.blueprint_get_size_x() >= 2048 or texture.blueprint_get_size_y() >= 2048) and texture.lod_group != texGroup:

            print(f'{asset.package_name} {texture.blueprint_get_size_x()}x{texture.blueprint_get_size_y()}')


if __name__ == '__main__':
    asset_list = []
    asset_list.extend(ListAssets('/Game/Buildings', ['Texture2D']))
    asset_list.extend(ListAssets('/Game/VFX', ['Texture2D']))
    asset_list.extend(ListAssets('/Game/Models', ['Texture2D']))
    asset_list.extend(ListAssets('/Game/Scence', ['Texture2D']))
    asset_list.extend(ListAssets('/Game/UI', ['Texture2D']))
    asset_list.extend(ListAssets('/Game/World', ['Texture2D']))

    CheckTextureSize(asset_list)