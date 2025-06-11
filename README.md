# my-notes-backend
使用Python程式語言與框架Flask實作「智慧學習筆記」後端RESTful API

# 如何開啟後端伺服器
在MacOS或Linux平台上可直接執行Repository裡的[start_server.sh](/start_server.sh)腳本，此腳本會自動生成Python的虛擬環境(`.venv`)並且使用Python語法：
```bash
cd ${PATH_TO}/my-notes-backend
./start_server.sh
```
在Windows平台則請參考該腳本自行下指令。

# 後端伺服器執行範例
- 使用HTTP GET方法在API拿到的回應：
    - ![API example](/screenshots/api_example.png)
- 伺服器執行時的日誌：
    - ![Server log](/screenshots/server_log.png)
