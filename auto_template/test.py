import os
from zipfile import ZipFile
import numpy as np
from lxml import etree
import xml.etree.ElementTree as ET
import zipfile
from docx import Document
import shutil
from langchain.llms.base import LLM
from typing import List, Optional
import requests
import json
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.llms import OpenAI
# from langchain.chains import RetrievalQA
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.document_loaders import TextLoader
# from langchain.vectorstores import FAISS
# from langchain.document_loaders import Docx2txtLoader
# from langchain.embeddings import HuggingFaceEmbeddings
from tool.auto_template_generate import is_normal_table,get_table_descible_template

class Vicuna(LLM):
    max_token: int = 2048
    temperature: float = 0.8
    top_p = 0.9
    tokenizer: object = None
    model: object = None
    history_len: int = 1024
    # url_llm = "https://u147750-b6ae-2bf49303.neimeng.seetacloud.com:6443/llm"
    url_llm = "https://u147750-92ae-0299e063.neimeng.seetacloud.com:6443/llm"

    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "Vicuna"

    def llm(self, prompt: str):
        try:
            content1 = json.dumps({"text": prompt})
            response = requests.request("POST", self.url_llm, data=content1)
            res = response.content.decode('unicode_escape')
            return json.loads(res, strict=False)['response']
        except:
            return "服务器已关闭，请联系服务器管理员"

    def _call(self, prompt: str, stop: Optional[List[str]] = None):
        response = self.llm(prompt)
        return response

def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')

def zip_dirs(*dirs,**kwargs):
    doc_filename=kwargs["doc_filename"]
    prefix = os.path.commonprefix(dirs)
    with ZipFile(doc_filename+'.zip', 'w') as z:
        for d in dirs:
            z.write(d, arcname=os.path.relpath(d, prefix))
            for root, dirs, files in os.walk(d):
                for fn in files:
                    z.write(
                        fp := os.path.join(root, fn),
                        arcname=os.path.relpath(fp, prefix)
                    )


def docx_to_xml(docx_path,xml_save_path):
    """
    :param docx_path:word文档路径
    :param xml_save_path:生成的xml文件保存路径
    :return:
    """
    doc = Document(docx_path)
    body_xml_str = doc._body._element.xml # 获取body中的xml
    body_xml = etree.fromstring(body_xml_str) # 转换成lxml结点
    # print(etree.tounicode(body_xml)) # 打印查看
    mode = 'w'
    with open(xml_save_path, mode,encoding='utf-8') as f:
        # string = string.encode('utf-8')
        f.write(etree.tounicode(body_xml))

def generate_table_description(table,table_describe_template,table_head_row_number,prefix):
    """

    :param table:
    :param table_describe_template: 表格描述模板
    :param table_head_row_number: 表格的表头行数
    :param prefix:word文档转换成xml后，某个标签属性的值需要prefix+标签才可以获取
    :return: 返回描述文本
    """

    all_rows=list(table.findall(prefix+"tr"))

    result=""

    value=[]
    for i in range(table_head_row_number,len(all_rows)):

        if len(list(all_rows[i].findall(prefix + "tc"))) < len(list(all_rows[i-1].findall(prefix + "tc"))):
            value=[]
            temp_value = ""
            for c in range(len(list(all_rows[i].findall(prefix + "tc")))):
                temp_value=""
                all_p = list(all_rows[i].findall(prefix + "tc"))[c].findall(prefix + "p")
                # print("p长度=", len(list(all_p)))

                if len(list(all_p)) == 0:
                    temp_value = "没填写内容"
                else:
                    for one_p in list(all_p):
                        all_r = list(one_p.findall(prefix + "r"))
                        for one_r in all_r:
                            if len(one_r.findall(prefix + "t")) > 0:
                                temp_value = temp_value + one_r.find(prefix + "t").text
                if not temp_value:
                    temp_value = "没填写内容"
                value.append(temp_value)
                arr = np.array(value)
            if (arr == "没填写内容").all():
                break
            result+="是".join(value)
            print(value)
            break
        r=i
        if i==table_head_row_number:
            value=[]
            for c in range(len(list(all_rows[i].findall(prefix + "tc")))):
                temp_value=""
                all_p = list(all_rows[r].findall(prefix + "tc"))[c].findall(prefix + "p")
                # print("p长度=", len(list(all_p)))

                if len(list(all_p)) == 0:
                    temp_value = "没填写内容"
                else:
                    for one_p in list(all_p):
                        all_r = list(one_p.findall(prefix + "r"))
                        for one_r in all_r:
                            if len(one_r.findall(prefix + "t")) > 0:
                                temp_value = temp_value + one_r.find(prefix + "t").text
                if not temp_value:
                    temp_value = "没填写内容"

                value.append(temp_value)
        else:
            for c in range(len(list(all_rows[i].findall(prefix + "tc")))):
                # print("j=",j)
                all_vMerge = list(all_rows[r].findall(prefix + "tc")[c].find(prefix + "tcPr").findall(
                    prefix + "vMerge"))

                if len(all_vMerge)>0 and (prefix + "val" not in all_vMerge[0].attrib or all_vMerge[0].attrib[prefix + "val"]=="continue"):
                    continue
                else:
                    temp_value=""
                    all_p=list(all_rows[r].findall(prefix+"tc"))[c].findall(prefix+"p")
                    # print("p长度=", len(list(all_p)))

                    if len(list(all_p)) == 0:
                        temp_value = "没填写内容"
                    else:
                        for one_p in list(all_p):
                            all_r=list(one_p.findall(prefix+"r"))
                            for one_r in all_r:
                                if len(one_r.findall(prefix + "t")) > 0:
                                    temp_value=temp_value+one_r.find(prefix+"t").text
                    if not temp_value:
                        temp_value = "没填写内容"

                    value[c]=temp_value
        print(value)
        arr = np.array(value)
        if (arr == "没填写内容").all():
            break
        # print(value)
        result += table_describe_template.format(*value)
        if len(list(all_rows[-1].findall(prefix + "tc")))==1:
            temp_value = ""
            all_p = list(all_rows[- 1].findall(prefix + "tc"))[0].findall(prefix + "p")
            # print("p长度=", len(list(all_p)))

            if len(list(all_p)) > 0:
                for one_p in list(all_p):
                    all_r = list(one_p.findall(prefix + "r"))
                    for one_r in all_r:
                        if len(one_r.findall(prefix + "t")) > 0:
                            temp_value = temp_value + one_r.find(prefix + "t").text
                result+=temp_value

    return result





def table_describe_to_doc(table_index,table_describe,complete_file_path):
    """
    用于把表格的描述模板插入到word文件中
    :param table_index: 表格在文档中的序号
    :param table_describe: 表格的描述文本
    :param complete_file_path: xml保存路径
    :return:
    """
    f=open(complete_file_path+"/word/document.xml",encoding='utf-8')
    file_str=f.read()
    f.close()

    index_temp=table_index
    start=-1
    while index_temp>0:
        start=file_str.find('<w:tbl>',start+1)
        index_temp-=1

    index_temp=table_index
    end=-1
    while index_temp>0:
        end=file_str.find('</w:tbl>',end+1)
        index_temp-=1
    end=end+7
    insertleft="""<w:p>
<w:pPr>
  <w:spacing w:line="360" w:lineRule="auto"/>
  <w:ind w:firstLine="480" w:firstLineChars="200"/>
  <w:rPr>
    <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    <w:sz w:val="24"/>
    <w:szCs w:val="24"/>
  </w:rPr>
</w:pPr>
<w:bookmarkStart w:id="40" w:name="_Toc83780989"/>
<w:bookmarkStart w:id="41" w:name="_Toc77646121"/>
<w:bookmarkStart w:id="42" w:name="_Toc415414318"/>
<w:r>
  <w:rPr>
    <w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>
    <w:sz w:val="24"/>
    <w:szCs w:val="24"/>
  </w:rPr>
  <w:t>"""
    insertright="""</w:t>
</w:r>
</w:p>"""
    inserttext=insertleft+table_describe+insertright
    new_file_str=file_str[:start]+inserttext+file_str[end+1:]
    with open(complete_file_path+"/word/document.xml",encoding='utf-8',mode="w") as f:
        f.write(new_file_str)
    pass


if __name__ == '__main__':
    all_files=os.listdir("./")
    doc_filename=""
    for file_name in all_files:
        if "docx" in file_name:
            doc_filename=file_name[:-5]
            break

    if not doc_filename:
        raise ValueError("没有要描述的文档")

    docx_path=doc_filename+".docx"
    # xml_save_path="tabel.xml"
    os.rename(doc_filename+".docx",doc_filename+".zip")
    unzip_file(doc_filename+".zip", doc_filename+"/")
    os.rename(doc_filename+".zip",doc_filename+".docx")
    shutil.copy(doc_filename+"/word/document.xml","document.xml")

    tree = ET.parse("document.xml")  # 类ElementTree
    root = tree.getroot()  # 类Element
    root_tag = root.tag
    i = len(root_tag) - 1

    while True:
        if root_tag[i] == "}":
            break
        i -= 1

    prefix = root_tag[:i + 1]
    body = root.find(prefix + "body")
    tables = list(body.findall(prefix + "tbl"))
    print(type(tables[0]))
    abnormal_table_count=0

    #对word中可进行自动化描述的表格进行处理
    for i,table in enumerate(tables):
        print("正在处理第"+str(i)+"个表")
        if is_normal_table(table,prefix):
            table_describe_template,table_head_row_number=get_table_descible_template(table,prefix)
            print("表格描述模板：",table_describe_template)
            print("表头行数：",table_head_row_number)

            table_describe=generate_table_description(table,table_describe_template,table_head_row_number,prefix)
            table_describe=table_describe.replace("<","小于").replace(">","大于")
            table_describe_to_doc(abnormal_table_count+1, table_describe, doc_filename)
            print((abnormal_table_count, table_describe))
            pass
        else:
            abnormal_table_count += 1

    ll = os.listdir(doc_filename)
    temp = []
    for ll_one in ll:
        temp.append(doc_filename+"/" + ll_one)
    zip_dirs(*temp,doc_filename=doc_filename)
    os.rename(doc_filename+".zip",doc_filename+"[描述后]"+".docx")

    os.remove("./document.xml")
    shutil.rmtree(doc_filename)











