#!/usr/bin/python3
#-*- coding: UTF-8 -*-
import os,sys
reload(sys)
sys.setdefaultencoding('utf8')
import getopt
import smtplib
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from  subprocess import *

def sendqqmail(username,password,mailfrom,mailto,subject,content):
    gserver = 'smtp.qq.com'
    gport = 25

    try:
        # msg = MIMEText(unicode(content).encode('utf-8')) //������͵��ʼ������룬���Գ��԰����иĳ����£�
        msg = MIMEText(content,'plan','utf-8') 
        msg['from'] = mailfrom
        msg['to'] = mailto
        msg['Reply-To'] = mailfrom
        msg['Subject'] = subject

        smtp = smtplib.SMTP(gserver, gport)
        smtp.set_debuglevel(0)
        smtp.ehlo()
        smtp.login(username,password)

        smtp.sendmail(mailfrom, mailto, msg.as_string())
        smtp.close()
    except Exception,err:
        print "Send mail failed. Error: %s" % err


def main():
    to=sys.argv[1]
    subject=sys.argv[2]
    content=sys.argv[3]
##����QQ������˺ź����룬����Ҫ�޸ĳ����Լ����˺ź����루�벻Ҫ����ʵ���û���������ŵ����Ϲ���������������ĺܲң�
    sendqqmail('liesun102@163.com','z6641916','liesun102@163.com',to,subject,content)

if __name__ == "__main__":
    main()
    
    
#####�ű�ʹ��˵��######
#1. ���ȶ���ýű��е������˺ź�����
#2. �ű�ִ������Ϊ��python mail.py Ŀ������ "�ʼ�����" "�ʼ�����"