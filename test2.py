from bioservices import KEGG
from collections import Counter
import urllib
import sys
import re
import os

def read_doc(filename):
    temp = open(filename, "r").read()
    temp = re.split('\t|\n',temp)
    temp = [x for x in temp if x != 'pp' and x != '']
    return temp

def format(group,compare):
    com = []
    a = group.split(',')
    b = compare.split(',')
    for pair in b:
        pair = pair.split(':')
        com.append(a[int(pair[0])-1]+ '-' + a[int(pair[1])-1])
    return com

def createFolder(name,com):
    os.mkdir('./%s'%name)
    for pair in com:
        os.mkdir('./%s/%s'%(name,pair))

def checkDownload(name,com):
    all = []
    al = os.listdir('./%s/%s'%(name,com))
    for name in al:
        nopng = name[3:8]
        all.append(nopng)
    print('Finish checking downloaded')
    return all

def checkOrg(org):
    if not os.path.exists('./%s_pathway.txt'%org):
        a = KEGG()
        b = a.list('pathway',org)
        with open('%s_pathway.txt'%org,'a',encoding='latin-1') as f:
            f.write(b)
        print('Finish writing org file')
    else:
        print('File already existed')

def getPathway(org,compare):
    temp = open('%s_pathway.txt' % org, "r").read()
    temp = re.findall(r'\d{5}', temp)
    text = read_doc('%s.txt'%compare)
    kegg_color = {};map = {};map_list = [];s = KEGG();final_com = {}
    for i in range(0,len(text)-1,2):
        newid = text[i] #'cpd:'+ text[i]
        kegg_color[newid] = text[i+1] + ',' + text[i+1]
    for id in kegg_color:
        a = s.get(id)
        dic = s.parse(a)
        try:
            if 'PATHWAY' in dic:
                map[id] = list(dic['PATHWAY'].keys())
                map_list.extend(map[id])
        except TypeError:
            print('Error:'+ a)
    final_map = dict(Counter(map_list))
    final_map = [x for x in final_map.items() if x[1] > 1]
    final_map = [x for x in final_map if x[0][3:] in temp]
    for pathway in final_map:
        newpath = pathway[0][3:]
        final_com[newpath] = []
        for compound in map:
            if pathway[0] in map[compound]:
                final_com[newpath].append(compound)
    return kegg_color,final_com

def downloadPathway(kegg_color,final_com,downloaded,pair):
    i = 1;s = KEGG()
    for path in final_com:
        if path not in downloaded:
            print('loading...%d'%i)
            i += 1
            keggid = dict([(key, kegg_color[key]) for key in final_com[path]])
            image_url = s.show_pathway("path:%s%s"%(org,path), dcolor="white",
                keggid=keggid)
            req = urllib.request.urlopen(image_url).read()
            req = req.decode()
            listurl = re.findall(r'tmp.*png', req)
            if path == '01100' or path == '01110':
                listurl = re.findall(r'tmp.*%s.{5}'%org,listurl[0])
                urll = listurl[0] + '.png'
                url = 'http://www.kegg.jp/' + urll
            else:
                url = 'http://www.kegg.jp/'+ listurl[0]
            f = open('./%s/%s/%s%s.png'%(client,pair,org,path), "wb")  # 打开文件
            req = urllib.request.urlopen(url)
            buf = req.read()  # 读出文件
            f.write(buf)  # 写入文件
            f.close()

if __name__ == '__main__':
    client = sys.argv[1]
    org = sys.argv[2]
    group = sys.argv[3]
    compare = sys.argv[4]
    checkOrg(org)
    com = format(group,compare)
    # createFolder(client,com)
    # print('Folders created')
    for pair in com:
        downloaded = checkDownload(client,pair)
        col,final = getPathway(org,pair)
        print('Downloading png')
        downloadPathway(col,final,downloaded,pair)
