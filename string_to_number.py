import os
import numpy as np
import requests
from lxml import etree
import hashlib
import matplotlib.pyplot as plt


def FetchMobileCPUNameList():
    
    # headers = {'user-agent': 'Mozilla/5.0 (windows NT 10.0; Win64; x64)AppleNebKit/537.36 (KHTML, like Gecko) chrome/85.0.4183.83'
    # }

    # url = r'https://www.notebookcheck.net/Smartphone-Processors-Benchmark-List.149513.0.html'
    # resp = requests.get(url, headers=headers)
    # result = resp.text
    # resp.close()

    # tree = etree.HTML(result)
    tree = etree.parse(r"./Smartphone Processors - Benchmark List - NotebookCheck.net Tech.html", etree.HTMLParser())

    tbody = tree.xpath('/html/body/main/div[2]/div/div[2]/div/div[2]/div/form/table')[0]

    num_header = 0
    total = 0

    model_names = []

    for row_elem in tbody.xpath('./tr'):
        total += 1

        if row_elem.get('class') == 'header':
            num_header += 1
            continue
        
        td = row_elem.xpath('./td')

        assert type(td) == list
        assert len(td) > 1 and total

        if len(td[1].xpath('./a')) == 0:
            model_name = td[1].text
        else:
            model_name = td[1].xpath('./a')[0].text

        model_names.append(model_name)

    print('num modlel names', len(model_names))

    # write model names to file
    # with open(r'd:\model_names.txt', 'w', encoding='utf-8') as file:
    #     for model_name in model_names:
    #         file.write(model_name + '\n')


    return model_names



def StringToHash(model_name : str):

    hash_value = ''

    m = hashlib.md5()
    m.update(model_name.encode())
    hash_value += m.hexdigest()

    # m = hashlib.sha256()
    # m.update(model_name.encode())
    # hash_value += m.hexdigest()

    # hash_value = hash_value[:20]

    code = [float(int(i, 16)) for i in hash_value]
    # print(code, type(code), type(code[0]))

    return code


def StringAndNumberFitting():
    mode_names = FetchMobileCPUNameList()
    mode_names = mode_names[:60]


    hash_values = []
    for model_name in mode_names:
        hash_value = StringToHash(model_name)
        hash_values.append(hash_value)

    hash_values = np.array(hash_values).astype(np.float32)
    print('hash', hash_values.shape)

    target_value = np.arange(len(mode_names), dtype=np.float32).reshape(-1, 1)
    
    x = np.linalg.inv(hash_values.T @ hash_values) @ hash_values.T @ target_value
    y = hash_values @ x


    #polt y points
    plt.plot(y)
    plt.plot(target_value)
    plt.show()




if __name__ == '__main__':
    # FetchMobileCPUNameList()

    # StringToHash("Apple M4 (10 cores)")

    StringAndNumberFitting()