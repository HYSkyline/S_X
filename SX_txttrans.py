# -*- coding:utf-8 -*-

import time
import sys
import re

reload(sys)
sys.setdefaultencoding('utf-8')
print u'程序环境编码:' + sys.getdefaultencoding()

print "Link Start!"
t0 = time.time()

fpath = r'D:\ctemp\S_X\targets\content.txt'
f = open(fpath, 'r')
content = f.readlines()
f.close()

# print content[3]
# print content[6]

trans01 = []
for each in content:
    if each.find("<") >= 0 or each.find(">") >= 0:
        trans01.append(re.sub('<.*?>', '', each))
    elif each.find('adsbygoogle') >= 0 or each.find('inline-block') >= 0 or each.find('data-ad-client') >= 0:
        pass
    elif each == '\r\n':
        pass
    else:
        trans01.append(each)

trans02 = []
for each in trans01:
    if each.find("<") >= 0:
        trans02.append(re.sub('<.*?\n', '', each))
    elif each.find(">") >= 0:
        trans02.append(re.sub('.*?>', '', each))
    elif each == '' or each == '\n' or each == '\r\n':
        pass
    elif each.find("，\n") >= 0:
        trans02.append(each.replace("，\n", ''))
    else:
        trans02.append(each.replace(' ', '').replace('\t', ''))

fpath = r'D:\ctemp\S_X\targets\trans.txt'
f = open(fpath, 'w')
for each in trans02:
    f.writelines(each)
f.close()

t1 = time.time()
time_cost = t1 - t0
print "Link Report:"
print u"程序运行时长%.3f" % float(time_cost) + u'秒.'
print ''
print 'Link Logout.'
