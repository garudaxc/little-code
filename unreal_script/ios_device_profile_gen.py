import re
import openpyxl
import subprocess

# i386 : iPhone Simulator
# x86_64 : iPhone Simulator
# arm64 : iPhone Simulator



class CodeInfo:
    def __init__(self, code_str):
        result = re.match(r'(\D+)(\d+),(\d+) : (.*)', code_str)
        if result:
            type, major, minor, name = result.groups()

        else:
            assert False, f'match code info failed {code_str}'

        self.type = type
        self.major = major
        self.minor = minor
        self.name = name

    def __str__(self):
        return f'{self.type} {self.major} {self.minor} {self.name}'
    

    def gen_match_string(self, grade):
    # +MatchProfile=(Profile="IOS_Grade1",TCQualityGrade="Grade1",Match=((StartWith="iPad",MajorBegin=0,MajorEnd=6,MinorBegin=0,MinorEnd=99)))
        s = f'+MatchProfile=(Profile="IOS_{grade}",TCQualityGrade="{self.name}",Match=((StartWith="{self.type}",MajorBegin={self.major},MajorEnd={self.major},MinorBegin={self.minor},MinorEnd={self.minor})))'
        return s


def gen_ios_device_profile():
    
    file_name = r"D:\小工具\device_profile_test\apple.xlsx"
    workbook = openpyxl.load_workbook(file_name)
    sheet = workbook['Sheet3']

    output_file = r"D:\小工具\unreal_script\ios_device_profile.txt"
    num_line = 0
    valid_line = 0
    with open(output_file, 'w') as f:
        match_string = r'+MatchProfile=(Profile="IOS_Grade5",TCQualityGrade="IOS_IPhone_NEW_UNKNOW",Match=((StartWith="iPhone",MajorBegin=0,MajorEnd=99,MinorBegin=0,MinorEnd=99)))'
        f.write(f'{match_string}\n')
        match_string = r'+MatchProfile=(Profile="IOS_Grade5",TCQualityGrade="IOS_IPad_NEW_UNKNOW",Match=((StartWith="iPad",MajorBegin=0,MajorEnd=99,MinorBegin=0,MinorEnd=99)))'
        f.write(f'{match_string}\n')
        for row in sheet.iter_rows(min_row=2, values_only=True):
            code, grade = row
            num_line += 1
            if grade is None:
                continue
            code_info = CodeInfo(code)
            match_string = code_info.gen_match_string(grade)
            f.write(f'{match_string}\n')
            valid_line += 1

    print(f'num_line {num_line} valid_line {valid_line}')

    

    # open output file
    subprocess.run(['start', output_file], shell=True)
    

    # for line in apple_device_code.split('\n'):
    #     if line.strip() == '':
    #         continue
        
    #     code_info = CodeInfo(line)

    #     print(code_info)




if __name__ == "__main__":
    gen_ios_device_profile()