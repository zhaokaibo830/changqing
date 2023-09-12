import os
from thefuzz import fuzz

#读取文件夹
file_path = 'D:/Files/2022/Programs/报告问答/files'
file_names = os.listdir(file_path)

#小测试
for file_name in file_names:
    print(file_name)

#子串匹配，使用匹配分数
str = '请描述杨加37-141A情况'
max_ratio=0
j = 0
for i in range(len(file_names)):
    pre_ratio = fuzz.ratio(str, file_names[i])
    if pre_ratio > max_ratio:
        max_ratio = pre_ratio
        j = i
print(file_names[j])



