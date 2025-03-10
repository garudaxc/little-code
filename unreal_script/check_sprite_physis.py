import unreal
import os
import sys

current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)
import unreal_utility


def Test():
    asset_dir = '/Game/UI/Atlas'
    type_name = ['PaperSprite']

    asset_list = unreal_utility.ListAssets(asset_dir, type_name)

    print('asset count:', len(asset_list))

    for asset_data in asset_list[:5]:
        asset_name = asset_data.package_name
        sprite = asset_data.get_asset()

        print(asset_name)

        # get collision domain
        collision = sprite.get_editor_property('SpriteCollisionDomain')
        print(collision)

        body_steup = sprite.get_editor_property('BodySetup')
        print(body_steup)

        sprite.set_editor_property('SpriteCollisionDomain', unreal.SpriteCollisionMode.NONE)


if __name__ == '__main__':
    Test()