import os
import subprocess
import requests
import re
import json
from lxml import etree
import time
import time

rul = r"https://www.ludashi.com/rank/index.html"
headers = ""



def make_unique_gpu_list(gpu_rank_list, keep_order=True):
    unique_list = list(set(gpu_rank_list))
    if len(unique_list) != len(gpu_rank_list):
        print(str(len(gpu_rank_list) - len(unique_list)), 'duplicated gpu in list')

    if keep_order:
        gpu_index = []
        for gpu_name in unique_list:
            gpu_index.append((gpu_name, gpu_rank_list.index(gpu_name)))

        gpu_index.sort(key = lambda x : x[1])

        unique_list = [item[0] for item in gpu_index]

    return unique_list


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


def generate_gpu_rank_ludashi():

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

    #save to file
    output_file = r"D:\小工具\profile\gpu_rank_list_ludashi.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(gpu_rank_list))
    
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
    


class GPUInfoScraper:
    def __init__(self):
        self.url = r"https://www.techpowerup.com/gpu-specs/?workstation=No&sort=name"
        self.headers = ""
        self.request_time = time.time()


    def batch_scrape(self, condition_list):
        
        big_list = []
        for Manufacuturer, ReleaseYear in condition_list:
                ReleaseYear = str(ReleaseYear)
                gpu_rank_list = self.scrape_gpu_rank(Manufacuturer=Manufacuturer, ReleaseYear=ReleaseYear)
                if gpu_rank_list:
                    big_list.extend(gpu_rank_list)
                else:
                    print('scrape failed ', Manufacuturer, ReleaseYear)

        big_list = make_unique_gpu_list(big_list)
        big_list.sort()

        #save to file
        # time_string = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        # with open(f"D:\小工具\profile\gpu_rank_list_{time_string}.txt", 'w', encoding='utf-8') as f:
        #     f.write('\n'.join(big_list))

        print('total gpus ', len(big_list))

    def scrape_gpu_rank(self, use_cache=True, Manufacuturer=None, ReleaseYear=None, time_interval=3):

        html_text = None

        #read from cache file
        cache_file = "D:\小工具\profile\cache\gpu_rank_cache%s%s.html" % ("_" + Manufacuturer if Manufacuturer else "", "_" + ReleaseYear if ReleaseYear else "")

        if use_cache and os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                html_text = f.read()
        else:
            url = self.url
            if Manufacuturer:
                url += f"&mfgr={Manufacuturer}"

            if ReleaseYear:
                url += f"&released={ReleaseYear}"

            while time.time() - self.request_time < time_interval:
                time.sleep(1)
            resp = requests.get(url=url, headers=self.headers)
            resp.close()
            self.request_time = time.time()
            if use_cache and resp.status_code == 200:
                os.remove(cache_file) if os.path.exists(cache_file) else None
                with open(cache_file, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                
                html_text = resp.text
            else:
                print('request failed')
                return

        # print('response ', len(resp.text))
        etree_html = etree.HTML(html_text)
        table_node = etree_html.xpath("//table[@class='processors']")[0]
        # print(table_node, len(table_node), table_node.tag)

        gpu_rank_list = []
        for tr_node in table_node.iterfind('./tr'):
            td_node = tr_node.find("./td[1]")[0]
            assert td_node
            vender = td_node.get('class')
            assert vender != '' and vender is not None
            print(vender)

            gpu_info_nodes = tr_node.xpath("./td[1]/a")
            if len(gpu_info_nodes) == 0:
                print('no gpu info')
                continue
            td_node = gpu_info_nodes[0]
            gpu_rank_list.append(td_node.text)
        
        gpu_rank_list = make_unique_gpu_list(gpu_rank_list)
        print('total gpus ', len(gpu_rank_list), gpu_rank_list[:5])

        return gpu_rank_list



def scrape_gpu_rank_from_TechPowerUp():

    scraper = GPUInfoScraper()

    contdition_list = []
    for Manufacuturer in ['NVIDIA', 'AMD', 'Intel']:
        for ReleaseYear in range(2010, 2026):
            contdition_list.append((Manufacuturer, ReleaseYear))

    for ReleaseYear in range(2010, 2014):
        contdition_list.append(('ATI', ReleaseYear))

    scraper.scrape_gpu_rank(use_cache=True, Manufacuturer='NVIDIA', ReleaseYear=2010)
    # scraper.batch_scrape(contdition_list)


    #save to file

def read_list_from_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip() != '']

        return lines


def cross_validate_gpu_rank():

    file_name_steam = r"D:\小工具\profile\GPU_name_steam.txt"
    gpu_list_steam = read_list_from_file(file_name_steam)
    
    gpu_list_ludashi = read_list_from_file(r"D:\小工具\profile\gpu_rank_list_ludashi.txt")

    gpu_list_techpowerup = read_list_from_file(r"D:\小工具\profile\gpu_rank_list.txt")

    count = 0
    for gpu_name in gpu_list_steam:
        if gpu_name not in gpu_list_ludashi:
            count += 1
            print('steam not in ludashi', gpu_name)

        # if gpu_name not in gpu_list_techpowerup:
        #     print('steam not in techpowerup', gpu_name)

    print('total gpu in steam ', len(gpu_list_steam), 'not in ludashi ', count)

    count = 0
    for gpu_name in gpu_list_steam:
        if gpu_name not in gpu_list_techpowerup:
            count += 1
            print('steam not in techpowerup', gpu_name)

    print('total gpu in steam ', len(gpu_list_steam), 'not in techpowerup ', count)


if __name__ == "__main__":
    # generate_gpu_rank()
    # cross_validate_gpu_rank()
    scrape_gpu_rank_from_TechPowerUp()