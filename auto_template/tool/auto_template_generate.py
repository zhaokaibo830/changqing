import xml.etree.ElementTree as ET
from collections import deque,defaultdict


class Node:
    """
    定义N叉树的节点
    """
    def __init__(self, val=None, children=None):
        self.val = val
        self.children = children

def is_normal_table(table,prefix):
    """
    判断table表格是否具有表头并且表头以下的每一行的列宽和表头最后一行是一致的
    :param table:table是表解析后的xml.etree.ElementTree.Element对象
    :param prefix:word文档转换成xml后，某个标签属性的值需要prefix+标签才可以获取
    :return:如果返回True表明具有表头并且表头以下的每一行的列宽和表头最后一行是一致的，可以进行自动化描述，否则不可以
    """

    #    all_row_column_weight存储所有列的列宽
    all_row_column_width = []
    all_row = list(table.findall(prefix + "tr"))
    # print("总过多少行：",len(all_row))

    # 不考虑最后一行，因为文档中很多表格最后一行是备注信息，这里做了特殊处理
    for one_row in all_row[:-1]:
        one_column_weight = []
        all_column = list(one_row.findall(prefix + "tc"))
        # print(len(all_column))
        for one_column in all_column:
            #xml中”w”属性是列宽
            weight = one_column.find(prefix + "tcPr").find(prefix + "tcW").attrib[prefix + "w"]
            if int(weight)==0:
                return False
            one_column_weight.append(int(weight))
        all_row_column_width.append(one_column_weight)

    # 满足要求的表格的充要条件是任意连续的两行内容，上一行的一个单元格精准分成了一个或者多个单元格，类似于树的结构
    for i in range(len(all_row_column_width) - 2):
        up_row, down_row = all_row_column_width[i], all_row_column_width[i + 1]
        print("i:",i)
        print("up_row",up_row)
        print("down_row",down_row)
        left = right = 0
        down_row_temp_sum = 0
        # print("i:",i)
        while left < len(up_row):
            # print("left",left)
            # print("right",right)
            down_row_temp_sum += down_row[right]
            if down_row_temp_sum < up_row[left]:
                right += 1
            elif down_row_temp_sum == up_row[left]:
                down_row_temp_sum = 0
                left, right = left + 1, right + 1
            else:
                return False
    return True

def buildTree(table,prefix):
    """
    如果表格符合树的结构，就对此表格构建N叉树。
    :param table:table是表解析后的xml.etree.ElementTree.Element对象
    :param prefix:word文档转换成xml后，某个标签属性的值需要prefix+标签才可以获取
    :return: 树的根节点、表头的行数、表格的第一行第一列是否有斜线、表格的第一行第一列的值
    """

    all_row_column_val_width = []
    all_row = list(table.findall(prefix + "tr"))
    # print("总共多少行：",len(all_row))
    is_have_tl2br=False
    one_row_one_column = []
    if len(all_row)>0:
        if len(list(all_row[0].findall(prefix + "tc")))>0:
            if len(list(all_row[0].findall(prefix + "tc"))[0].findall(prefix + "tcPr"))>0:
                if len(list(list(list(all_row[0].findall(prefix + "tc"))[0].findall(prefix + "tcPr"))[0].findall(prefix + "tcBorders")))>0:
                    if len(list(list(list(list(all_row[0].findall(prefix + "tc"))[0].findall(prefix + "tcPr"))[0].findall(prefix + "tcBorders"))[0].findall(prefix + "tl2br")))>0:
                        #表格的第一行第一列有斜线，让is_have_tl2br为True
                        is_have_tl2br = True
                        all_p=list(all_row[0].findall(prefix + "tc"))[0].findall(prefix + "p")
                        for one_p in all_p:
                            temp_value=""
                            all_r = list(one_p.findall(prefix + "r"))
                            for one_r in all_r:
                                # print(one_r.find(prefix + "t"))
                                if len(one_r.findall(prefix + "t")) > 0:
                                    # print(one_r.find(prefix + "t").text)
                                    temp_value = temp_value + one_r.find(prefix + "t").text
                            one_row_one_column.append(temp_value)
                        print(one_row_one_column)

    table_head_row_number=0
    #获取表头每一行中单元格的值以及列宽
    for i,one_row in enumerate(all_row[:-1]):
        one_column_val_width = []
        all_column = list(one_row.findall(prefix + "tc"))
        # print(len(all_column))
        for one_column in all_column:
            weight = one_column.find(prefix + "tcPr").find(prefix + "tcW").attrib[prefix + "w"]


            temp_value = ""
            all_p=one_column.findall(prefix + "p")
            if len(list(all_p)) == 0:
                temp_value = ""
            else:
                for one_p in list(all_p):
                    all_r = list(one_p.findall(prefix + "r"))
                    for one_r in all_r:
                        # print(one_r.find(prefix + "t"))
                        if len(one_r.findall(prefix + "t"))>0:
                            # print(one_r.find(prefix + "t").text)
                            temp_value = temp_value + one_r.find(prefix + "t").text


            one_column_val_width.append((temp_value,(int(weight))))
        all_row_column_val_width.append(one_column_val_width)
        if i>=1 and len(all_row_column_val_width[-1])==len(all_row_column_val_width[-2]):
            table_head_row_number=i
            break
        table_head_row_number = len(all_row_column_val_width)
    # print(all_row_column_val_weight)
    # print("表头行数：",table_head_row_number)

    root_children=[]
    d1=deque()

    #先对第一行构建树
    for first_column_val,_ in all_row_column_val_width[0]:
        node=Node(first_column_val)
        # print(first_column_val)
        root_children.append(node)
        d1.append(node)

    #如果表格的第一行第一列有斜线需要对第一行第一列的表头做特殊处理
    if is_have_tl2br and len(one_row_one_column)>=1:
        root_children[0].val=one_row_one_column[1]

    root=Node("",root_children)


    temp_queue=[]

    #依据层次遍历构建树
    for j_row in range(1,table_head_row_number):
        up_row, down_row = all_row_column_val_width[j_row-1], all_row_column_val_width[j_row]
        left = right = 0
        while d1:
            pop_node=d1.popleft()
            if up_row[left][1]==down_row[right][1]:
                temp_queue.append(pop_node)
                left,right=left+1,right+1
            else:
                down_row_temp_sum = 0
                children=[]
                while down_row_temp_sum < up_row[left][1]:
                    # print(down_row[right][0])
                    subnode=Node(down_row[right][0])
                    children.append(subnode)
                    temp_queue.append(subnode)
                    down_row_temp_sum += down_row[right][1]
                    right += 1
                pop_node.children=children
                left = left+1
        d1=deque(temp_queue)
        temp_queue=[]
    return root,table_head_row_number,is_have_tl2br,one_row_one_column



def get_table_descible_template(table,prefix):
    """
    利用N叉树的非递归遍历算法获取每个叶子节点的所有祖先节点序列，根据这些序列生成表格描述模板
    :param table:table是表解析后的xml.etree.ElementTree.Element对象
    :param prefix:word文档转换成xml后，某个标签属性的值需要prefix+标签才可以获取
    :return: 表格描述模板、表头的行数
    """
    root,table_head_row_number,is_have_tl2br,one_row_one_column=buildTree(table,prefix)
    if root is None:
        return []
    ans = ""
    st = []
    nextIndex = defaultdict(int)
    node = root
    while st or node:
        while node:
            # ans.append(node.val)
            # print(node.val)
            st.append(node)
            if not node.children:
                for ss in st[1:-1]:
                    ans=ans+ss.val.replace(" ","")+"的"
                if is_have_tl2br and len(one_row_one_column)>=2 and ans:
                    ans = ans + st[-1].val.replace(" ", "") + one_row_one_column[0]+"是{},"
                else:
                    ans=ans+st[-1].val.replace(" ","")+"是{},"
            if not node.children:
                break
            nextIndex[node] = 1
            node = node.children[0]
        node = st[-1]
        i = nextIndex[node]
        if node.children and i < len(node.children):
            nextIndex[node] = i + 1
            node = node.children[i]
        else:
            st.pop()
            del nextIndex[node]
            node = None
    ans = ans[:-1]+"。"
    return ans,table_head_row_number






if __name__ == '__main__':
    tree = ET.parse("document.xml")  # 类ElementTree
    root = tree.getroot()  # 类Element
    root_tag = root.tag
    i = len(root_tag) - 1

    while True:
        if root_tag[i] == "}":
            break
        i -= 1

    prefix = root_tag[:i + 1]
    print(prefix)

    body = root.find(prefix + "body")
    tbl = list(body.findall(prefix + "tbl"))[18]
    # one_row=list(tbl.findall(prefix + "tr"))[4]
    # one_c=list(one_row.findall(prefix + "tc"))[0]
    # a=one_c.find(prefix + "tcPr").find(prefix + "tcW").attrib[prefix + "type"]

    # print(tbl)
    a=is_normal_table(tbl,prefix)
    print(a)
    if a:

        ans=get_table_descible_template(tbl,prefix)
        print(ans)







