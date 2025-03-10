from P4 import P4,P4Exception,Spec    # Import the module


class P4Wrapper:
    def __init__(self) -> None:
        self.p4 = P4()
        try:
            self.p4.connect()
            print('perforce connect succeeded')
        except P4Exception as e:
            print(e)


    def IsSynced(self, file):
        '''
        文件是否同步到了最新
        '''
        synced = False

        try:
            res = self.p4.run_sync('-n', file)
        except P4Exception as e:
            synced = True
        
        if not synced:
            res = res[0]
            if type(res) == dict and res['action'] == 'updated':
                synced = False

            else:
                assert False, 'Unexpected result: %s' % res

        return synced


    def IsOpenedForEdit(self, file):
        '''
        文件是否打开
        '''
        opened = False
        try:
            res = self.p4.run_opened('-a', file)
        except P4Exception as e:
            opened = True

        if not opened:
            res = res[0]
            if type(res) == dict and res['action'] == 'edit':
                opened = True

            else:
                assert False, 'Unexpected result: %s' % res

        return opened


    def IsLocalModified(self, file):
        '''
        文件是否有修改
        '''
        try:
            res = self.p4.run_status(file)
        except P4Exception as e:
            return False

        if type(res) == list and len(res) == 0:
            return False
        
        res = res[0]
        assert type(res) == dict, f'{file} test modify Unexpected result: {res}'

        if res['action'] == 'edit':
            return True
        
        else:
            print(f"{file} test modify result: { res['action'] }")
            return False


    def Checkout(self, file):
        try:            
            res = self.p4.run_edit(file)
            return True
        except P4Exception as e:
            print(e)
            return False
    
    # def CreateChangeList(self, description = 'my changelist'):   
    #     try:
    #         new_changelist = self.p4.fetch_change()

    #         # new_changelist = self.p4.run_change('-o')
    #         new_changelist['Description'] = description
    #         # result = self.p4.save_change(new_changelist)

    #         # [print(i) for i in dir(new_changelist)]
    #         print(type(new_changelist))

    #         for key, value in new_changelist.items():
    #             print(f"{key}: {type(value)}")

    #         print(type(new_changelist._Files[0]))
    #         print(new_changelist._Change)

    #         print(new_changelist.permitted_fields())

    #         # print("变更列表创建成功，编号为:", result)
    #         # return result
    #     except P4Exception as e:
    #         print("出现错误:", e)

    #         return False

    def CreateChangeList(self, file_list : list, description = 'my changelist'):
        fields = {'change': 'Change', 'client': 'Client', 'user': 'User', 'status': 'Status', 'type': 'Type', 'identity': 'Identity', 'description': 'Description', 'files': 'Files'}
        spec = Spec(fields)
        
        spec._change = 'new'
        spec._Description = description

        depot_files = []
        for local_file_path in file_list:

            depot_path_info = self.p4.run_fstat(local_file_path)

            if depot_path_info:
                depot_path = depot_path_info[0]
                depot_path = depot_path['depotFile']

                depot_files.append(depot_path)
            else:
                print("无法找到本地路径对应的depot路径")
                continue

        spec._Files = depot_files
        try:
            result = self.p4.save_change(spec)
            print("变更列表创建成功，编号为:", result)
            return result
        except P4Exception as e:
            print("出现错误:", e)
            return None


if __name__ == '__main__':

    file = r'd:\ka1_client\client\trunk\BeyondStar\Content\PublishResources\cfg\setting\setting_config.lua'
    file = r'd:\ka1_client\client\trunk\BeyondStar\Content\PublishResources\lua\product\ui\panel\common\ui_view_common_item.lua'
    file = r'd:\ka1_client\client\trunk\BeyondStar\Content\TestAsset\xuchao\LSZZ\Mesh\775.uasset'
    file = r'd:\ka1_client\client\trunk\BeyondStar\Content\TestAsset\xuchao\LSZZ\Mesh\868.uasset'
    file = r'D:/ka1_client/client/trunk/BeyondStar/Content/Buildings/K02/K02_F/K02_Tree_Oasis_01.uasset'

    p4 = P4Wrapper()

    # res = p4.run_edit(file)
    res = p4.p4.run_status(file)
    print(res)

    '''
    LogPython: [{'depotFile': '//art/trunk/BeyondStar/Content/PublishResources/cfg/setting/setting_config.lua', 'clientFile': 'd:\\ka1_client\\client\\trunk\\BeyondStar\\Content\\PublishResources\\cfg\\setting\\setting_config.lua', 'localFile': 'd:\\ka1_client\\client\\trunk\\BeyondStar\\Content\\PublishResources\\cfg\\setting\\setting_config.lua', 'workRev': '7
    3', 'action': 'edit', 'type': 'unicode'}, '//art/trunk/BeyondStar/Content/PublishResources/cfg/setting/setting_config.lua - must sync/resolve #74 before submitting']
    '''


    # res = p4.run_sync('-n', file)
    # res = p4.run_sync(file)

    # res = IsSynced(file)
    # res = p4.IsLocalModified(file)
    # res = p4.Checkout(file)
    # print(res)

    # p4.CreateChangeList2()

