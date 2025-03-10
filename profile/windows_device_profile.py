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


output_file = r"D:\小工具\unreal_script\gen_pc_device_profile.txt"

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

def read_list_from_file(file_name, stript_band=False):
    with open(file_name, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines if line.strip() != '']

        if stript_band:
            lines = [line.removeprefix('ATI ').removeprefix('Intel ').removeprefix('NVIDIA ').removeprefix('AMD ') for line in lines]

        return lines


class GPUName:
    def __init__(self, name, rank = -1):
        self.rank = rank
        
        bands = ['Intel(R)', 'ATI', 'Intel', 'NVIDIA', 'AMD']
        # self.band = []

        if name.startswith('Intel '):
            name = name.replace('Intel ', 'Intel(R) ')

        self.with_ti = False
        self.with_SUPER = False
        self.laptop = False
        self.with_series = False
        self.with_memory = False
        self.with_maxQ = False
        while True:
            # for band in bands:
            #     if name.startswith(band):
            #         name = name.removeprefix(band).strip()
            #         self.band.append(band)

            dumy_match = re.match(".*?(?=\s+Graphics)$", name)
            if dumy_match:
                name = dumy_match.group(0).strip()
                continue

            mem_match = re.match(".*(?=\s+\d\d?GB?$)", name)
            maxQ_match = re.match(".*?(?=\s+(with\s+)?Max-Q.*)", name)
            laptop_match = re.match(".*?(?=\s+\(Laptop\))", name)
            if name.endswith('Ti'):
                name = name.removesuffix('Ti').strip()
                self.with_ti = True
                continue
            elif name.endswith('SUPER'):
                name = name.removesuffix('SUPER').strip()
                self.with_SUPER = True
                continue
            elif name.endswith('Super'):
                name = name.removesuffix('Super').strip()
                self.with_SUPER = True
                continue
            elif name.endswith('Laptop GPU'):
                name = name.removesuffix('Laptop GPU').strip()
                self.laptop = True
                continue
            elif laptop_match:
                name = laptop_match.group(0).strip()
                self.laptop = True
                continue
            elif name.endswith('Series'):
                name = name.removesuffix('Series').strip()
                self.with_series = True
                continue
            elif mem_match:
                name = mem_match.group(0).strip()
                self.with_memory = True
                continue
            elif maxQ_match:
                name = maxQ_match.group(0).strip()
                self.with_maxQ = True
                continue
            else:
                break

        
        self.name = name
        
        flag = 0
        if self.with_ti:
            flag |= 1
        if self.with_SUPER:
            flag |= 2
        if self.laptop:
            flag |= 4
        # if self.with_series:
        #     flag |= 8
        # if self.with_memory:
        #     flag |= 32
        if self.with_maxQ:
            flag |= 64

        self.flag = flag

        self.match_string = self.make_match_string()

    def full_match(self, other):
        return self.name == other.name and self.flag == other.flag        
    
    def __str__(self):        

        return '[%s] [flag %x] [rank %d]' % (self.name, self.flag, self.rank)
    
    def __eq__(self, other):
        return self.name == other.name

    def set_score(self, score):
        self.score = score

    def make_match_string(self):        

        match_string = f"{self.name}"
        match_string = match_string.replace('(', '\\(').replace(')', '\\)').replace('-', '\\-')
        
        if self.with_ti:
            match_string += ' Ti'
        if self.with_SUPER:
            match_string += ' (?:SUPER)|(?:Super)'
        if self.laptop:
            match_string += ' Laptop GPU'
        if self.with_maxQ:
            match_string += ' with Max\\-Q(?: Design)?'

        return match_string

    def final_match_string(self):
        return f'+MatchProfile=(Profile=GST_GPU, Score={self.score}, Match=((SourceType=SRC_GpuFamily, CompareType=CMP_Regex, MatchString=\"{self.match_string}\")))'

def add_handmaade_gpu_rank(gpu_list):

    def add(gpu_name, flag, rank):
        found = False
        for gpu in gpu_list:
            if gpu.name == gpu_name and gpu.flag == flag:
                gpu.rank = rank
                found = True
                break

        if not found:
            # print(f'gpu [{gpu_name}] not found')
            gpu = GPUName(gpu_name, rank)
            gpu.flag = flag
            gpu_list.append(gpu)

    # 手动你添加一些常用的gpu, rank值来自于notebookcheck排名
    # https://www.notebookcheck.net/Smartphone-Graphics-Cards-Benchmark-List.149363.0.html
    add("NVIDIA GeForce RTX 5090", 0, 1)
    add("NVIDIA GeForce RTX 5080", 0, 3)
    add("NVIDIA GeForce RTX 5070 Ti", 0, 5)
    add("NVIDIA GeForce RTX 3050", 1, 140)
    add("NVIDIA GeForce GTX 1650", 1, 215)
    add("NVIDIA GeForce RTX 2050", 0, 227)
    add("NVIDIA GeForce GTX 750", 0, 400)
    add("NVIDIA GeForce GTX 260", 0, 550)

    add("Intel(R) Arc(TM)", 0, 200)
    add("Intel(R) Iris(R) Xe", 0, 350)
    add("Intel(R) Iris(R)", 0, 550)

    add("NVIDIA GeForce 8800 GTX", 0, 600)
    add("NVIDIA GeForce 9500 GT", 0, 1000)
    add("NVIDIA GeForce 9600 GT", 0, 900)
    add("NVIDIA GeForce 9800 GT", 0, 650)
    add("NVIDIA GeForce GTS 250", 0, 1000)
    add("NVIDIA GeForce 8400 GS", 0, 1000)
    add("NVIDIA GeForce 9400 GT", 0, 1000)
    add("NVIDIA GeForce G210", 0, 1000)
    add("NVIDIA GeForce 8600 GT", 0, 1000)
    
    add("AMD Radeon(TM) Vega 3 Graphics", 0, 700)
    add("AMD Radeon(TM) Vega 8 Graphics", 0, 500)
    add("AMD Radeon RX 550", 0, 400)
    add("NVIDIA GeForce GT 730", 0, 600)
    add("NVIDIA GeForce GTX 650", 0, 500)
    add("NVIDIA GeForce GT 240", 0, 670)
    add("NVIDIA GeForce 210", 0, 1000)

    add("NVIDIA GeForce GTX 550 Ti", 0, 476)
    add("NVIDIA GeForce GT 620", 0, 809)
    add("NVIDIA T600 Laptop GPU", 0, 258)
    add("NVIDIA GeForce GT 740", 0, 554)
    add("NVIDIA GeForce 820A", 0, 720)
    add("NVIDIA Quadro P2200", 0, 250)
    add("NVIDIA Quadro T2000 with Max-Q Design", 0, 241)
    add("NVIDIA Quadro P620", 0, 361)
    add("NVIDIA GeForce MX110", 0, 564)
    add("NVIDIA Quadro P2000", 0, 285)
    add("NVIDIA GeForce GT 720", 0, 725)

    add("AMD Radeon RX 580 2048SP", 0, 200)
    add("AMD Radeon RX590 GME", 0, 202)

    add("Radeon 520", 0, 626)
    add("Radeon RX 560", 0, 332)

    add("Radeon(TM) RX 460 Graphics", 0, 327)
    add("Radeon RX 550X", 0, 362)
    add("Radeon RX 580 Series", 0, 203)
    add("Radeon RX 570 Series", 0, 209)
    add("Radeon (TM) RX 470 Series", 0, 247)
    
    add("AMD  Radeon RX 7800 XT", 0, 24)
    add("AMD Radeon RX 6750 GRE", 0, 54)
    add("AMD Radeon 780M Graphics", 0, 276)
    add("AMD Radeon R5 M200 / HD 8500M Series", 0, 730)

    add("AMD Radeon R7 Graphics", 0, 400)
    add("AMD Radeon R7 200 Series", 0, 400)
    add("AMD Radeon (TM) R9 380 Series", 0, 279)

    add("AMD Radeon(TM) Graphics", 0, 500)
    add("NVIDIA Graphics Device", 0, 999)
    add("Intel(R) HD Graphics", 0, 1000)
    add("Intel(R) UHD Graphics", 0, 800)

    add("Mirage Driver", 0, 999)
    add("Virtual Display Adapter", 0, 999)
    add("Virtual Display Device", 0, 999)
    add("GameViewer Virtual Display Adapter", 0, 999)








# 生成pc端的gpu匹配规则
def generate_pc_gpu_rank():

    file_name_steam = r"D:\小工具\profile\GPU_name_steam.txt"
    gpu_list_steam = read_list_from_file(file_name_steam)

    gpu_list_tencent = read_list_from_file(r"D:\小工具\profile\gpu_name_tencent.txt")


    gpu_list = []

    def collect_gpu_list(gpu_list, gpu_names):

        for gpu_name in gpu_names:
            other = GPUName(gpu_name)
            matched = False
            for gpu in gpu_list:
                if gpu.full_match(other):
                    matched = True
                    break
            if not matched:
                gpu_list.append(other)

    #以steam,和腾讯大盘为基准
    collect_gpu_list(gpu_list, gpu_list_steam)
    collect_gpu_list(gpu_list, gpu_list_tencent)

    
    #save to file
    # output_file = r"D:\小工具\profile\gpu_name_list.txt"
    # with open(output_file, 'w', encoding='utf-8') as f:
    #     f.write('\n'.join([str(i) for i in gpu_list]))

    # for gpu_name in gpu_list:
    #     if gpu_name not in gpu_list_steam:
    #         print('[%s] not in steam' % gpu_name)
    #     print(gpu_name)

    # ludashi_rank_list = []
    # collect_gpu_list(ludashi_rank_list, gpu_list_ludashi)

    # 性能评分以notebookcheck排名为准
    gpu_list_notebookcheck = read_list_from_file(r"D:\小工具\profile\gpu_rank_notebookcheck.txt")
    rank_notebook = []
    for index, gpu_name in enumerate(gpu_list_notebookcheck):
        rank_notebook.append(GPUName(gpu_name, index))


    def find_gpu_rank(gpu, rank_list):
        for rank_gpu in rank_list:
            if rank_gpu.full_match(gpu):
                return rank_gpu.rank
        return -1
    
    add_handmaade_gpu_rank(gpu_list)

    count = 0
    for gpu in gpu_list:

        # for other in rank_notebook:
        #     if gpu.name != other.name and gpu.name.find(other.name) != -1:
        #         print(f'[{gpu.name}] match [{other.name}]')
        #         count += 1

        rank = find_gpu_rank(gpu, rank_notebook)
        if rank != -1:
            gpu.rank = rank

        # if rank == -1 and gpu.rank == -1:
        #     print('%d %s' % (count, str(gpu)))
        #     count += 1

    # print gpu with rank -1
    # for gpu in gpu_list:
    #     if gpu.rank == -1:
    #         print(gpu.name)


    #sort by rank
    gpu_list = [gpu for gpu in gpu_list if gpu.rank != -1]
    gpu_list.sort(key=lambda x: x.rank)

    # set score
    count = len(gpu_list)        
    for index, gpu in enumerate(gpu_list):
        gpu.set_score(count - index)
    
    gpu_list.sort(key=lambda x: x.match_string, reverse=False)

    #save to file
    with open(output_file, 'w', encoding='utf-8') as f:

        
        #分档基线
        baseline_grade2 = 'NVIDIA GeForce GTX 960'
        baseline_grade3 = 'NVIDIA GeForce RTX 3060'

        score_grade2 = list(filter(lambda x: x.name == baseline_grade2 and x.flag == 0, gpu_list))[0].score
        score_grade3 = list(filter(lambda x: x.name == baseline_grade3 and x.flag == 0, gpu_list))[0].score

        f.write('\n;WindowsGradeScoreProfileName\n')
        f.write(r'[/Script/WindowsDeviceProfileSelector.WindowsGradeScoreProfileName]')
        f.write('\n')
        f.write('+MatchProfile=(Profile="Windows_Grade1",TCQualityGrade="Grade01",Score=-100)\n')
        f.write('+MatchProfile=(Profile="Windows_Grade2", TCQualityGrade="Grade02", Score=%d)\n' % score_grade2)
        f.write('+MatchProfile=(Profile="Windows_Grade3", TCQualityGrade="Grade03", Score=%d)\n' % score_grade3)

        f.write('\n;按字符串排序，从短到长匹配\n')
        f.write(r'[/Script/WindowsDeviceProfileSelector.WindowsGradeMatchProfileRules]')
        f.write('\n')
        for gpu in gpu_list:
            str = gpu.final_match_string()
            f.write(f'{str}\n')


        print('done output to file ', output_file)
        subprocess.run(['start', output_file], shell=True)


if __name__ == "__main__":
    # generate_gpu_rank()
    # scrape_gpu_rank_from_TechPowerUp()

    #生成pc端
    generate_pc_gpu_rank()
    
    # maxQ_match = re.match(".*?(?=\s+(with\s+)?Max-Q.*)", 'NVIDIA GeForce RTX 3060 with Max-Q')
    # print(f'\'{maxQ_match.group(0)}\'')


    # laptop_match = re.match(".*?(?=\s+\(Laptop\))", 'NVIDIA GeForce GTX 980 (Laptop)')
    # print(f'\'{laptop_match.group(0)}\'')

    # dumy_match = re.match(".*?(?=\s+Graphics)", 'Radeon Vega 8 Graphics')
    # print(f'\'{dumy_match.group(0)}\'')

