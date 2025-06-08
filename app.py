# 檔名: app.py
# 匯入 Flask Web 框架及相關工具
from flask import Flask, request, jsonify
# 匯入 CORS，解決前後端不同源的請求問題
from flask_cors import CORS

# 初始化 Flask 應用程式
app = Flask(__name__)
# 設定 CORS，允許所有來源的請求，方便本機開發
CORS(app)

# --- 暫時性的資料儲存區 ---
# 在這個 MVP 階段，我們先不用資料庫，直接用一個 Python 的 list 來模擬。
# 伺服器重啟後，資料就會消失，這在下一階段會用資料庫來解決。
notes = [
    {
        "id": 1,
        "subject": "微積分",
        "content": "複習第一章的極限定義。"
    },
    {
        "id": 2,
        "subject": "Python",
        "content": "學習 Flask 框架如何建立RESTful API。"
    },
    {
        "id": 3,
        "subject": "英文",
        "content": "背 10 個新的單字。"
    }
]
# 用來產生新筆記的唯一 ID
next_id = 4

# --- API 路由 (Endpoints) ---

# 路由 1: 取得所有筆記
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """
    處理 GET 請求，回傳目前所有的筆記列表。
    前端頁面一載入時，就會呼叫這個 API。
    """
    print("接收到 GET /api/notes 請求，回傳筆記列表。")
    return jsonify(notes)

# 路由 2: 新增一筆筆記
@app.route('/api/notes', methods=['POST'])
def add_note():
    """
    處理 POST 請求，從請求的 body 中取得新筆記的資料，
    然後將它新增到我們的 notes 列表中。
    """
    global next_id # 宣告我們要修改全域變數 next_id
    # 從前端請求的 JSON body 中獲取資料，如果沒有則回傳空字典
    new_note_data = request.get_json(silent=True)

    # 簡單的驗證，確保 content 欄位存在
    if not new_note_data or 'content' not in new_note_data or 'subject' not in new_note_data:
        # 如果資料不完整，回傳錯誤訊息
        return jsonify({"error": "資料不完整，需要 'subject' 和 'content' 欄位"}), 400

    # 建立一筆新的筆記
    note = {
        "id": next_id,
        "subject": new_note_data['subject'],
        "content": new_note_data['content']
    }
    notes.append(note)
    next_id += 1 # ID 加一，為下一筆做準備

    print(f"接收到 POST /api/notes 請求，新增筆記: {note}")
    # 回傳剛新增的筆記，並附上 HTTP 狀態碼 201 (表示已建立)
    return jsonify(note), 201

# --- 啟動伺服器 ---
# 確保這個腳本是直接被執行，而不是被匯入的
if __name__ == '__main__':
    # 啟動 Flask 應用程式，並在 5000 port 上運行
    # debug=True 會在程式碼變動時自動重啟伺服器
    app.run(host='0.0.0.0', port=8080, debug=True)
