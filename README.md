# HTTP File Server

**http-file-server** 是用 python 实现的 HTTP 文件服务器，支持上传和下载文件。

## 运行

```bash
$ python file-server.py files 8001
```

其中第一个参数 `files` 是存放文件的路径，第二个参数 `8001` 是 HTTP 服务器端口。

## 接口

### 1. 读取文件

```
GET /pathtofile/filename
```

### 2. 读取文件夹下所有文件（已经忽略隐藏文件）

```
GET /path
```
返回文件列表为 `JSON` 数组，文件名末尾带有 `/` 的表示是文件夹。
`filename` 为文件名，`mtime` 为修改时间。

```json
[{"filename":"f1.txt","mtime":1001},{"filename":"p3/","mtime":1002}]
```

### 3. 上传文件

curl  -F "filename=@jenkins.war" http://ip:port/upload\?name\=tmp2/jenkins1.war

采用 `POST` 方式上传文件，`URL` 参数中传参数 `name` 表示上传的文件名，`POST` 内容为文件内容。
```
POST /upload?name=filename
```

`ajax` 示例:
```js
// file is a FileReader object
var data = file.readAsArrayBuffer();
var xhr = new XMLHttpRequest();
var url = "http://localhost:8001/upload?name=xxx.md";
xhr.open("post", url, true);
xhr.setRequestHeader("Accept", "application/json, text/javascript, */*; q=0.01");
xhr.onreadystatechange = function() {
  if (xhr.readyState==4 && xhr.status==200)
  {
    console.log(xhr.responseText);
  }
}
xhr.send(data);
```

文件名 filename 可以包含相对路径。比如：`upload?name=md/xxx.md`。则上传至 `md` 目录下。
