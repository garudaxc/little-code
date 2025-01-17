import subprocess
import requests
import re
import json
from lxml import etree

rul = r"https://www.ludashi.com/rank/index.html"
headers = ""



def make_unique_gpu_list(gpu_rank_list):
    unique_list = list(set(gpu_rank_list))
    if len(unique_list) != len(gpu_rank_list):
        print(str(len(gpu_rank_list) - len(unique_list)), 'duplicated gpu in list')

    gpu_index = []
    for gpu_name in unique_list:
        gpu_index.append((gpu_name, gpu_rank_list.index(gpu_name)))

    gpu_index.sort(key = lambda x : x[1])

    new_list = [item[0] for item in gpu_index]

    return new_list


def read_gpu_rank(file_path):

    
    # resp_ = requests.get(url=rul, headers=headers)
    # resp = resp_.text
    # resp_.close()

    # print('response ', len(resp))
    
    # #save to file
    # with open(r"D:\小工具\profile\鲁大师天梯榜.html", 'w', encoding='utf-8') as f:
    #     f.write(resp)

    with open(file_path, 'r', encoding='utf-8') as f:
        resp = f.read()

    tree = etree.HTML(resp)
    list_head = tree.xpath("//div[@id='main-count-list-data']")[0]

    gpu_rank_list = []
    # 匹配最后的显存文字
    gpu_match = re.compile(r'.*(?=\s+\d+(G|M)B$)')

    for child in list_head.iterfind('./div'):
        score_item = child.find("./div")
        assert score_item is not None
        score_string = score_item.get("data-score", "0")
        score = int(score_string)
        assert score > 0

        data_item = child.find("./div/p[@class='main-count-list-code-p']")
        assert data_item is not None
        gpu_string = data_item.text.strip()
        match = gpu_match.match(gpu_string)
        if match:
            if match.group(0) == 'NVIDIA GeForce GPU':
                print('invalid gpu name', gpu_string, score)
                continue

            gpu_rank_list.append((match.group(0), score))
        else:
            if re.match(r'^NVIDIA GeForce RTX 3050 (4|6)GB Laptop GPU$', gpu_string):
                gpu_rank_list.append((gpu_string, score))
            else:
                print("unmatched gpu : ", gpu_string)

    # print(gpu_rank_list[:5])

    return gpu_rank_list


def generate_gpu_rank():

    list_pc = read_gpu_rank(r"D:\小工具\profile\鲁大师天梯榜.html")
    list_laptop = read_gpu_rank(r"D:\小工具\profile\鲁大师榜单-笔记本.html")

    print(f"num pc gpu : {len(list_pc)}, num laptop gpu : {len(list_laptop)}")

    gpu_rank_list = list_pc
    gpu_rank_list.extend(list_laptop)

    gpu_rank_list.sort(key = lambda x : x[1], reverse=True)
    gpu_rank_list = [item[0] for item in gpu_rank_list]

    gpu_rank_list = make_unique_gpu_list(gpu_rank_list)
    gpu_rank_list.reverse()
    print('total gpus ', len(gpu_rank_list))

    
    output_file = r"D:\小工具\unreal_script\pc_device_profile.txt"
    num_line = 0
    with open(output_file, 'w') as f:
        # match_string = r'+MatchProfile=(Profile="IOS_Grade5",TCQualityGrade="IOS_IPhone_NEW_UNKNOW",Match=((StartWith="iPhone",MajorBegin=0,MajorEnd=99,MinorBegin=0,MinorEnd=99)))'
        # f.write(f'{match_string}\n')
        # match_string = r'+MatchProfile=(Profile="IOS_Grade5",TCQualityGrade="IOS_IPad_NEW_UNKNOW",Match=((StartWith="iPad",MajorBegin=0,MajorEnd=99,MinorBegin=0,MinorEnd=99)))'
        # f.write(f'{match_string}\n')
        for gpu_name in gpu_rank_list:
            num_line += 1
            profile_string = f'+MatchProfile=(Profile=GST_GPU,Score={num_line},Match=((SourceType=SRC_GpuFamily,CompareType=CMP_Equal,MatchString=\"{gpu_name}\")))'
            f.write(f'{profile_string}\n')


    print('done')
    
    subprocess.run(['start', output_file], shell=True)
    

if __name__ == "__main__":
    generate_gpu_rank()