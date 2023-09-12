import random
import time

f=open("1.txt",encoding='utf-8')
text=f.readline()
while text:
    input("请输入您想要问的问题：")
    time.sleep(random.randint(2,6))
    print("AI:",text)
    text=f.readline()
