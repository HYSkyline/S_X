# -*- coding:utf-8 -*-
import urllib
import urllib2
import gzip
from StringIO import StringIO
import re
import time
import sys
import threading

reload(sys)
sys.setdefaultencoding('utf-8')
print u"当前环境编码:" + sys.getdefaultencoding()


def main():         # 主体程序部分
    confirm = input(u"目标网站数据量较大,程序运行时间可能较长\n在程序运行期间需要保证网络畅通\n输入0,回车开始运行.\n")
    # confirm = 0
    if confirm == 0:
        pass
    else:
        exit(0)
    threadnum = input(u'输入线程数\n更多线程代表更快速度以及更高的计算资源占用(推荐值:8)\n')
    # threadnum = 8
    print "Link Start!"
    t0 = time.time()
    list_urls = list_next()
    # list_urls = ['http://www.xinxiaowang.com/tag/11/451.html']            # 测试单页读取
    thread_init(list_check, list_urls, threadnum)

    target_list = target_read()
    thread_init(target_fetch, target_list, threadnum)

    apath = r"D:\ctemp\S_X\targets\page_errors.txt"
    bpath = r"D:\ctemp\S_X\targets\target_error.txt"
    error_num = error_read(apath) + error_read(bpath)
    # report(t0, len(target_list), error_num)
    report(t0, len(target_list), error_num)


def thread_init(function, mission_list, threadnum):
    threadpool = []
    thread_partresult_list = []
    function_list = thread_distribute(mission_list, threadnum)
    global lock
    lock = threading.Lock()
    threadcode = 0
    for i in range(0, threadnum):
        threadcode += 1
        t = threading.Thread(target=function, args=[function_list[i], threadcode])
        threadpool.append(t)
    for t in threadpool:
        t.start()
    for t in threadpool:
        t.join()
    return 0


def thread_distribute(mission_list, threadnum):
    function_list = [[] for i in range(0, threadnum)]
    for i in range(0, len(mission_list)):
        index = i % threadnum
        function_list[index].append(mission_list[i])
    return function_list


def list_next():            # 读取列表网页的所有页面URL
    print u"当前事件:list_next"
    list_url = []

    init_url = 'http://www.xinxiaowang.com/tag/11/2.html'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
    postdata = {
        'User_Agent': user_agent
    }
    data = urllib.urlencode(postdata)
    req = urllib2.Request(
        init_url,
        data
    )

    response = urllib2.urlopen(req)
    html = response_gzip(response)
    response.close()

    list_url_search = '" class="a2" target="_self">下一页</a><a href="(.*?)" class="a1" target="_self">尾页</a></div>'
    try:
        list_url_init = re.findall(list_url_search, html, re.S)
        final_url = list_url_init[0]
        final_pagenum_search = '/tag/11/(.*?).html'
        final_pagenum = re.findall(final_pagenum_search, final_url)[0]

        # final_pagenum = 32

        for i in range(1, int(final_pagenum) + 1):
            url = 'http://www.xinxiaowang.com/tag/11/' + str(i) + '.html'
            list_url.append(url)
        print u'----------总页数读取完成,准备分析各页中的目标地址.------------'
    except Exception as e:
        print u'总页数读取失败,错误来源于' + str(e)
        print u'程序准备退出.'
        exit(100)
    return list_url


def list_check(list, code):           # 传入列表网页每一页的URL,读取当前列表网页的所有目标URL
    # print u"当前事件:list_check"
    targets = []
    errors = []
    for i in range(0, len(list)):
        page_url = list[i]
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
        postdata = {
            'User_Agent': user_agent
        }
        data = urllib.urlencode(postdata)
        req = urllib2.Request(
            page_url,
            data
        )
        try:
            response = urllib2.urlopen(req)
            html = response_gzip(response)
            response.close()
        except Exception as e:
            print u'来自第' + str(code) + u'线程报告:' + u'第' + str(i + 1) + u'页登入失败,本页无法读取.错误来自于' + str(e)
            errors.append(u'第' + str(code) + u'线程:' + u'第' + str(i + 1) + u'页登入失败,本页无法读取.错误来自于' + str(e))
            continue

        try:
            target_search = '<div class="list_title"><a href="(.*?)">.*?</a></div>'
            target_init = re.findall(target_search, html, re.S)
            for each in target_init:
                targets.append('http://www.xinxiaowang.com' + each)
            print u'来自第' + str(code) + u'线程报告:' + u"第" + str(i + 1) + u'页分析完成.(' + str(i + 1) + '/' + str(len(list)) + ')'
        except Exception as e:
            print u'来自第' + str(code) + u'线程报告:' + u'第' + str(i + 1) + u'页分析失败,错误来自于' + str(e)
            errors.append(u'第' + str(code) + u'线程报告:' + u'第' + str(i + 1) + u'页分析失败,错误来自于' + str(e))
    print u'---------------线程' + str(code) + u':所有目标URL读取完成---------------'

    if lock.acquire():
        fpath = r"D:\ctemp\S_X\targets\target.txt"
        f = open(fpath, 'a')
        for each in targets:
            f.writelines(each)
            f.writelines('\n')
        f.close()

        fpath = r"D:\ctemp\S_X\targets\page_errors.txt"
        f = open(fpath, 'a')
        for each in errors:
            f.writelines(each)
            f.writelines('\n')
        f.close()

        lock.release()
    return targets


def target_read():
    fpath = r"D:\ctemp\S_X\targets\target.txt"
    f = open(fpath, 'r')
    targets = f.readlines()
    print ''
    return targets


def target_fetch(targets, code):         # 读取目标具体内容
    # print u"当前事件:target_fetch"
    errors = []
    for i in range(0, len(targets)):
        init_url = targets[i]
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
        postdata = {
            'User_Agent': user_agent
        }
        data = urllib.urlencode(postdata)
        req = urllib2.Request(
            init_url,
            data
        )
        try:
            response = urllib2.urlopen(req)
            html = response_gzip(response)
            response.close()
        except Exception as e:
            print u'来自第' + str(code) + u'线程报告:' + u'第' + str(i + 1) + u'个目标登入失败,目标数据无法读取.错误来自于' + str(e)
            errors.append(u'第' + str(code) + u'线程:' + u'第' + str(i + 1) + u'个目标登入失败,目标数据无法读取.错误来自于' + str(e))
            continue

        try:
            title_search = '<h2>(.*?)</h2>'
            content_search = '<div class="nr_note">(.*?)</div>'
            title_init = re.findall(title_search, html, re.S)
            content_init = re.findall(content_search, html, re.S)
            if content_init[0].find('img') >= 0:
                target_photosave(title_init[0], content_init[0], i + 1)
            else:
                target_txtsave(title_init[0], content_init[0], i + 1)
            print u'来自第' + str(code) + u'线程报告:' + u"第" + str(i + 1) + u'个目标读取完成.(' + str(i + 1) + '/' + str(len(targets)) + ')'
        except Exception as e:
            print u'来自第' + str(code) + u'线程报告:' + u'第' + str(i + 1) + u'个目标读取失败,错误来自于' + str(e)
            errors.append(u'第' + str(code) + u'线程:' + u'第' + str(i + 1) + u'个目标读取失败,错误来自于' + str(e))
            continue

    if lock.acquire():
        fpath = r"D:\ctemp\S_X\targets\target_error.txt"
        f = open(fpath, 'a')
        for each in errors:
            f.writelines(each)
            f.writelines('\n')
        f.close()
        lock.release()
    print u'------------------线程' + str(code) + u'所有目标读取完成---------------------'
    return 0


def target_txtsave(title, content, i):           # 存储文本信息
    # print u"当前事件:target_txtsave"

    if lock.acquire():
        fpath = r"D:\ctemp\S_X\targets\content.txt"
        # print u"存储目录:" + fpath
        f = open(fpath, 'a')
        content_correct = content.replace('<p>', '').replace('</p>', "\n")
        # print u"写入标题:" + title
        # print u"写入内容:" + content_correct
        f.writelines(title)
        f.writelines('\n')
        f.writelines(content_correct)
        f.writelines('\n')
        f.writelines('\n')
        f.close()
        lock.release()
    return 0


def target_photosave(title, content, i):
    # print u"当前事件:target_photosave"
    photourl_search = '<img alt="" src="(.*?)"/>'
    photourl_init = re.findall(photourl_search, content, re.S)
    photourl = 'http://www.xinxiaowang.com' + photourl_init[0]
    try:
        response = urllib2.urlopen(photourl)
        image = response_gzip(response)
        fpath = 'D:\\ctemp\\S_X\\targets\\img\\' + title.decode('utf-8').encode('gbk') + '.jpg'
        f = open(fpath, 'wb')
        f.write(image)
        f.close()
    except Exception as e:
        print u"图片型目标析出失败,错误来自于" + str(e)
    return 0


def error_read(fpath):
    f = open(fpath, 'r')
    errors = f.readlines()
    return len(errors)


def report(t0, num, errornum):           # 程序报告
    t1 = time.time()
    time_cost = t1 - t0
    print ''
    print "Link Report:"
    print u"程序运行时长:%.3f" % float(time_cost) + u"秒."
    print u'总计有效目标' + str(num) + u'个,完成其中' + str(num - errornum) + u'个.完成率%.3f' % float(float(num - errornum)/num * 100) + '%'
    print ''
    return 0


def response_gzip(response):            # 对网页的gzip压缩进行解读
    if response.info().get('content-encoding') == 'gzip':
        buf = StringIO(response.read())
        f = gzip.GzipFile(fileobj=buf)
        gzip_data = f.read()
    else:
        gzip_data = response.read()
    return gzip_data


if __name__ == '__main__':
    main()
