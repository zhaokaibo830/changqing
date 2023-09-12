# -*- coding:utf-8 -*-
import random
import time
import traceback
from flask import Flask, jsonify,request,make_response
from gevent import pywsgi
from funcs.q2a import ReportQA,start
import requests
import json
import config
from PIL import Image
from io import BytesIO
import base64

app = Flask(__name__)
app.config.from_object(config)



# no safety check, without select sentence matching
@app.route('/api/v2/report_qa',methods=['post'])
def report_qa():

    time.sleep(2)
    # global qa
    get_data = request.get_data()
    print(type(get_data))
    print(get_data)
    get_data = json.loads(get_data)
    question = get_data['question']
    print("question:",question)
    out = {}
    out['error'] = ""
    out['queryStatus'] = 1
    out['data'] = {}
    try:

        out['data']["file"] = "《乾133-17钻井地质设计报告》"
        out['data']['image'] = ""

        if "压力剖面图" in question:
            out['data']["answer"] ="帮您找到了乾133-17井的层三压力剖面，如下图所示:"
            with open("image/压力剖面图.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            out['data']['image'] = encoded_string
            out['data']['page']=26
        elif "地貌" in question:
            out['data']["answer"] = "井区属典型的黄土塬地貌，地面海拔1005～1694m。"
            out['data']['page'] = 4
        elif "气候" in question:
            out['data']["answer"] = "区内属黄土地貌，第四系黄土覆盖厚度25～230m，泾河水系之上游马莲河、蒲河流经油田东西两侧，次级支流呈树枝状，地形比较复杂。气候干旱，工业用水开采层为宜君组、洛河组，单位产水量大约17-27m3/h，水质差，矿化度大于3.2g/l。"
            out['data']['page'] = 4
        elif "地质构造" in question:
            out['data']["answer"] = "区域上属陕北斜坡西南段，局部构造位于庆阳鼻褶带，构造形态为西倾单斜。"
            out['data']['page'] = 5
        elif "有毒有害气体" in question:
            out['data']["answer"] = "目前暂未监测到CO、H2S等有毒有害气体。"
            out['data']['page'] = 7
        elif "压力系数" in question:
            out['data']["answer"] = "乾133-17井的地层压力系数是0.82。"
            with open("image/压力系数.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            out['data']['image'] = encoded_string
            out['data']['page'] = 12
        elif "钻头尺寸" in question:
            out['data']["answer"] = "井身的油层套管的钻头尺寸是215.9×井底（mm×m）。"
            with open("image/钻头尺寸.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            out['data']['image'] = encoded_string
            out['data']['page'] = 14
        elif "取心原则" in question:
            # answer = ReportQA(qa, question)
            out['data']["answer"] = """以下是帮您找到的取心原则：
（1）绥36油层段全分析卡层取心，要求穿鞋带帽，取心收获率≥95%；
（2）做好邻井对比，卡准取心层位，发现地层变化较大时，立即向项目组汇报，进一步确定取心井段；
（3）接近取心层位时，每0.2m记录钻时，如钻时明显加快，及时进行地质循环，并向项目组汇报。
            """
            out['data']['page'] = 15
        elif "直罗组" in question and "井段" in question:
            # answer = ReportQA(qa, question)
            out['data']["answer"] = "直罗组的井段在1110m到井底。如下表所示:"

            with open("image/直罗组井段.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            out['data']['image'] = encoded_string
            out['data']['page'] = 15
        elif "钻井液" in question:
            out['data']["answer"] = "钻井液类型为清水聚合物的对应洛河、安定、直罗层位。"
            out['data']['page'] = 13
        elif "井控风险井" in question:
            out['data']["answer"] = """满足以下条件之一的为二级井控风险井。
（1）105MPa>预测地层压力≥70MPa；（2）100×104m3/d>预测单井天然气无阻流量≥30×104m3/d；（3）30g/m3（20000ppm）>预测硫化氢含量≥1.5g/m3（1000ppm）；（4）6000m>垂深≥4500m的井；（5）4500m>垂深≥2000m的区域探井、预探井；（6）气相欠平衡、控压钻井，重大新工艺、新技术试验井。满足以上条件之一的为二级井控风险井。"""
            out['data']['page'] = 18
        elif "破裂压力" in question:
            out['data']["answer"] = "乾133-17的破裂压力是32.6MPa。"
            with open("image/破裂压力.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            out['data']['image'] = encoded_string
            out['data']['page'] = 11
        elif "气温" in question:
            out['data']["answer"] = "年平均气温为9.6℃～11.9℃。"
            out['data']['page'] = 4
        elif "原油粘度" in question:
            out['data']["answer"] = "地面原油粘度是10.24mpa•s。"
            out['data']['page'] = 7
        elif "中靶坐标" in question:
            out['data']["answer"] = "中靶的纵坐标X是4047902，横坐标Y是36482471。"
            out['data']['page'] = 9
        else:
            # answer = ReportQA(qa, question)
            out['data']["answer"] = "很抱歉，我不知道。"
            out['data']["file"] = "无参考文档"
            out['data']['page'] = 0

        out['queryStatus'] = 0


    except Exception as e:
        out['error'] = traceback.format_exc()
        print(e)
    return jsonify(out)

# @app.route('/api/get_image',methods=['post'])
# def get_image():
#     get_data = request.get_data()
#     print(type(get_data))
#     print(get_data)
#     get_data = json.loads(get_data)
#     image_name = get_data['image_name']
#     try:
#         # 打开一张图片
#         image_path = './压力剖面图.png'
#         with open(image_path, 'rb') as f:
#             image_data = f.read()
#             image = Image.open(BytesIO(image_data))
#         # 转化为二进制流
#         img_io = BytesIO()
#         image.save(img_io,'JPEG')
#         img_io.seek(0)
#         # 返回二进制流
#         response = make_response(img_io.getvalue())
#         response.headers['Content-Type'] = 'image/jpeg'
#         return response
#
#
#     except Exception as e:
#         response="出错"
#     return response


if __name__ == '__main__':

    # qa=start()

    if config.USE_WSGI_SERVER:
        server = pywsgi.WSGIServer((config.FLASK_RUN_HOST,config.FLASK_RUN_PORT),app)
    else:
        app.run(debug=True,host=config.FLASK_RUN_HOST,port=config.FLASK_RUN_PORT)
    # server = pywsgi.WSGIServer(('127.0.0.1',8810),app)
    # server.serve_forever()
