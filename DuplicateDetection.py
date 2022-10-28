from ast import For
import jieba
import gensim
import re
import os
import sys

pyFileDataSet = []

# 得到当前目录下所有的文件
def getALLSamplePyFile(path, sp=""):
    filesList = os.listdir(path)

    # 处理每一个文件
    sp += " "
    for fileName in filesList:
        # 判断一个文件是否为目录(用绝对路径)  join拼判断接法
        fileAbsPath = os.path.join(path, fileName)
        if os.path.isdir(fileAbsPath):  # 临界条件： 如果不是目录 执行else
            # print(sp + "目录：",fileName)
            getALLSamplePyFile(fileAbsPath, sp)  # 递归调用 自己调用自己
        else:
            isPyFile = fileName.endswith(".py")
            if isPyFile:
                pyFileDataSet.append(fileAbsPath)
                # print(sp + "py文件：",fileAbsPath)


# 获取指定路径的文件内容
def get_file_contents(path):
    string = ""
    f = open(path, "r", encoding="UTF-8")
    line = f.readline()
    while line:
        string = string + line
        line = f.readline()
    f.close()
    return string


# 将读取到的文件内容先把标点符号、转义符号等特殊符号过滤掉，然后再进行结巴分词
def filter(string):
    pattern = re.compile("[^a-zA-Z0-9\u4e00-\u9fa5]")
    string = pattern.sub("", string)
    result = jieba.lcut(string)
    return result


# 传入过滤之后的数据，通过调用gensim.similarities.Similarity计算余弦相似度
def calc_similarity(text1, text2):
    texts = [text1, text2]
    dictionary = gensim.corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    similarity = gensim.similarities.Similarity(
        "-Similarity-index", corpus, num_features=len(dictionary)
    )
    test_corpus_1 = dictionary.doc2bow(text1)
    cosine_sim = similarity[test_corpus_1][1]
    return cosine_sim


def run_calc(originFilePath, destFilePath):
    if not os.path.exists(originFilePath):
        print("原文文件不存在")
        exit()
    if not os.path.exists(destFilePath):
        print("待检测文件不存在")
        exit()
    str1 = get_file_contents(originFilePath)
    str2 = get_file_contents(destFilePath)
    text1 = filter(str1)
    text2 = filter(str2)
    similarity = calc_similarity(
        text1, text2
    )  # 生成的similarity变量类型为<class 'numpy.flo at32'>
    result = round(
        similarity.item(), 2
    )  # 借助similarity.item()转化为<class 'float'>，然后再取小数点后两位
    return result


if __name__ == "__main__":
    """
    & C:/Users/Method-Jiao/AppData/Local/Programs/Python/Python310/python.exe c:/Users/Method-Jiao/Documents/DuplicateDetection/DuplicateDetection.py 'C:\\Program Files (x86)\\BIMBase建模软件 2023\\PythonScript\\ParamComponentLib' "C:\\Users\\Method-Jiao\\Documents\\DuplicateDetection\\3.py"
    """
    if len(sys.argv) == 3:
        sampleDir = sys.argv[1]
        destFile = sys.argv[2]

        getALLSamplePyFile(sampleDir)  # 需要遍历的path

        for pyFile in pyFileDataSet:
            similarity = run_calc(pyFile, destFile)
            if similarity > 0.9:
                print("代码相似度：", similarity, "相重文件路径：", pyFile)
                break
    else:
        getALLSamplePyFile(
            r"C:\Program Files (x86)\BIMBase建模软件 2023\PythonScript\ParamComponentLib"
        )  # 需要遍历的path
        for pyFile in pyFileDataSet:
            similarity = run_calc(
                pyFile, r"C:\Users\Method-Jiao\Documents\DuplicateDetection\3.py"
            )
            if similarity > 0.9:
                print("代码相似度：", similarity, "相重文件路径：", pyFile)
                break

    # 将相似度结果写入指定文件
    # f = open(save_path, 'w', encoding="utf-8")
    # f.write("代码相似度： %.4f"%similarity)
    # f.close()
