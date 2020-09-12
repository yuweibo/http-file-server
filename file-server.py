#!/usr/bin/env python
# coding: utf-8

import os
import sys
import urllib
import codecs
import glob
import commands
import time
import re
import BaseHTTPServer
import SocketServer
import mimetypes
import json

reload(sys)
sys.setdefaultencoding("utf-8")
mimetypes.init()

g_filepath = ""


def transDicts(params):
    dicts = {}
    if len(params) == 0:
        return
    params = params.split("&")
    for param in params:
        keyvalue = param.split("=")
        key = keyvalue[0]
        value = keyvalue[1]
        value = urllib.unquote_plus(value).decode("utf-8", "ignore")
        dicts[key] = value
    return dicts


class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("access-control-allow-origin", "*")
        BaseHTTPServer.BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        query = urllib.splitquery(self.path)
        path = urllib.unquote_plus(query[0]).decode("utf-8", "ignore")
        queryParams = {}
        print path

        if "?" in self.path:
            if query[1]:
                queryParams = transDicts(query[1])

        fn = "%s%s" % (g_filepath, path)
        fn = urllib.unquote_plus(fn).decode("utf-8", "ignore")
        fn = fn.replace("/", os.sep)

        content = ""
        self.send_response(200)
        self.send_header("content-type", "application/json")
        if os.path.isfile(fn):
            if(queryParams.has_key("op") and queryParams["op"] == "d"):
                f = open(fn, 'rb')
                file_data = f.read()
                f.close()

                self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                self.wfile.write(file_data)
                self.send_response(200)
                return
            f = open(fn, "rb")
            content = f.read().decode('utf-8')
            f.close()
            contenttype, _ = mimetypes.guess_type(fn)
            if contenttype:
                self.send_header("content-type", contenttype+";charset=utf-8")
        elif os.path.isdir(fn):
            filelist = []
            for filename in os.listdir(fn):
                if filename[0] != ".":
                    filepath = "%s%s%s" % (fn, os.sep, filename)
                    if os.path.isdir(filepath):
                        filename += os.sep
                    mtime = os.path.getmtime(filepath)
                    isfile = os.path.isfile(filepath)
                    filelist.append(
                        {"filename": filename, "mtime": mtime, "isfile": isfile})
                    filelist = sorted(
                        filelist, key=lambda e: e.__getitem__('mtime'))

            # content html
            self.send_header("content-type", "text/html")
            content += "<head><meta charset=\"UTF-8\"></head>"
            content += "<html><body>"
            content += "<h2>Directory listing for "+path+"</h2>"
            content += "<hr>"
            content += "<ul>"
            for o in filelist:
                content += "<li>"+time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(o["mtime"]))+"-"+o["filename"]
                content += "<a href=\""+path + \
                    o["filename"]+"\">" + \
                    "<input type=\"button\" value=\"view\">"+"</a>"
                content += ("" if(o["isfile"] != True) else "<a href=\""+path +
                            o["filename"]+"?op=d\">" +
                            "<input type=\"button\" value=\"download\">"+"</a>")
                content += "</li>"

            content += "</ul>"
            content += "<hr>"
            content += "</body></html>"
            # content json
            # content = json.dumps(filelist)
        else:
            print(g_filepath, path, fn)
            content = "<h1>404<h1>"
            self.send_header("content-type", "text/html")

        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        query = urllib.splitquery(self.path)
        path = query[0]
        queryParams = {}

        if "?" in self.path:
            if query[1]:
                queryParams = transDicts(query[1])

        resultdict = {"result": 0, "msg": "OK"}
        if path == "/upload":
            if queryParams.has_key("name"):
                filesize = int(self.headers["content-length"])
                filecontent = self.rfile.read(filesize)
                fn = queryParams["name"]
                resultdict["filename"] = fn
                fn = "%s%s" % (g_filepath, fn)
                dirname = os.path.dirname(fn)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                if os.path.isdir(fn):
                    resultdict.result = 1
                    resultdict.msg = "File name is directory."
                else:
                    f = open(fn, "wb")
                    f.write(filecontent)
                    f.close()
            else:
                resultdict.result = 2
                resultdict.msg = "Need file name."
        else:
            resultdict.result = 3
            resultdict.msg = "No this API."

        content = json.dumps(resultdict)
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(content)


class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass


def run(port):
    print "HTTP File Server Started at port:", port
    server_address = ("", port)
    httpd = ThreadingHTTPServer(("", port), HTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    g_filepath = "./files/"
    if len(sys.argv) >= 2:
        g_filepath = sys.argv[1]
    if g_filepath[-1] != os.sep:
        g_filepath += os.sep
    g_filepath = g_filepath.replace("/", os.sep)

    port = 8000
    if len(sys.argv) == 3:
        port = int(sys.argv[2])

    run(port)
