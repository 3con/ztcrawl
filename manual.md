#中投在线文章爬虫
###安装

#####windows
1.安装python时请安装pip(python2.7, openssl)
2.安装scrapy(爬虫框架), Pillow(缩略图)
```
pip install scrapy
pip install Pillow
```
3.安装pywin32, 在[官网](http://python.org/download/)下载python和主机架构对应的版本

#####Ubuntu
1.python2.7
2.OpenSSL
```
apt-get install libssl-dev
```
3.lxml(libxml2, libxstl)
```
apt-get install python-lxml
```
4.scrapy, pillow, pyOpenssl

#####CentOS([scrapyd](http://scrapyd.readthedocs.org/en/latest/))
1.默认python版本2.6.6, 需要升级为2.7以上
```
cd
wget http://python.org/ftp/python/2.7.3/Python-2.7.3.tar.bz2
tar -jxvf Python-2.7.3.tar.bz2
yum install openssl-devel sqlite-devel -y
```
2.在编译前需要修改配置
```
vim /root/Python-2.7.3/Modules/Setup.dist
```
3.替换
```
# Socket module helper for socket(2) 
_socket socketmodule.c timemodule.c 
# Socket module helper for SSL support; you must comment out the other 
# socket line above, and possibly edit the SSL variable: #SSL=/usr/local/ssl 
_ssl _ssl.c \-DUSE_SSL -I$(SSL)/include -I$(SSL)/include/openssl \ 
            -L$(SSL)/lib -lssl -lcrypto
```
4.安装python
```
./configure 
make all 
make install
```
```
# 修复sqlite
cp ./build/lib.linux-x86_64-2.7/_sqlite3.so /usr/local/lib/python2.7/lib-dynload
make clean 
make distclean
```
5.2.6->2.7
```
mv /usr/bin/python /usr/bin/python2.6.6
ln -s /usr/local/bin/python2.7 /usr/bin/python
```
6.修复yum
```
vim /usr/bin/yum

#!/usr/bin/python
#!/usr/bin/python2.6.6
```
7.安装libffi
```
yum install libffi-devel
```
8.安装pip, scrapy, scrapyd, scrapyd-client
```
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

pip install scrapy
pip install pillow
pip install scrapyd
pip install scrapyd-client
pip install redis
```


###使用

1.不启用scrapyd, 根目录运行
```
scrapy runspider /ztcrawl/spiders/(爬虫名称.py)
```
2.启用scrapyd
```
cd /root
mkdir ztcrawl # ztcrawl为scrapyd的文件目录
cd ztcrawl
scrapyd > running.log # 可直接断开终端 tail -f running.log查看日志 
```
切换到项目目录
```
scrapyd-deploy -p ztcrawl
```
可直接运行以下命令, 或将以下命令写入crontab, localhost可为主机IP
```
curl http://localhost:6800/schedule.json -d project=ztcrawl -d spider=(爬虫名称)
```

4.爬虫结合缓存使用, 若调试时记录已被爬过, 该记录会被drop, 缓存清空方法, 运行`remove.py`
```
python remove.py
# 或者
python remove.py (爬虫名称)
```

###用supervisor后台运行scrapyd
```
pip install supervisor
echo_supervisord_conf > /etc/supervisord.conf
cp /etc/supervisord.conf /root/ztcrawl
vim /root/ztcrawl/supervisord.conf
```
附加配置
```
[inet_http_server]
port = 0.0.0.0:9001
username = admin
password = ztol

[program:scrapyd]
command=scrapyd
autostart=true
```
最后启动supervisor
```
supervisord -c supervisord.conf
```
iptables(9001 supervisor 6800 scrapyd)
```
iptables -I INPUT -p tcp -m tcp --dport 9001 -j ACCEPT
iptables -I INPUT -p tcp -m tcp --dport 6800 -j ACCEPT
```
###crontab
```
30 8 * * * curl http://localhost:6800/schedule.json -d project=ztcrawl -d spider=easymoney
31 8 * * * curl http://localhost:6800/schedule.json -d project=ztcrawl -d spider=cnstock
32 8 * * * curl http://localhost:6800/schedule.json -d project=ztcrawl -d spider=pedaily
33 8 * * * curl http://localhost:6800/schedule.json -d project=ztcrawl -d spider=hexun
34 8 * * * curl http://localhost:6800/schedule.json -d project=ztcrawl -d spider=simuwang
```