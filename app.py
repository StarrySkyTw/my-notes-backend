# 檔名: app.py
# 匯入 Flask Web 框架及相關工具
import os
from flask import Flask, request, jsonify
# 匯入 CORS，解決前後端不同源的請求問題
from flask_cors import CORS
# 匯入 SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# 初始化 Flask 應用程式
app = Flask(__name__)

# --- CORS 設定修正 ---
# 將原本簡單的 CORS(app) 改為更明確的資源設定。
# 這會告訴 Flask-CORS 主動為所有 /api/ 開頭的路由處理 OPTIONS 預檢請求，
# 從而解決 Flask 路由系統搶先回傳 404 的問題。
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- 資料庫設定 ---
# 設定資料庫連線的 URI。
# 這邊以 PostgreSQL 為例。請將 '使用者名稱', '密碼', '主機位置', '資料庫名稱' 替換成你自己的設定。
# 範例: 'postgresql://postgres:mysecretpassword@localhost/mynotes'
# 如果你想用 MySQL，可以改成:
# 'mysql+pymysql://使用者名稱:密碼@主機位置/資料庫名稱'
# 例如: 'mysql+pymysql://root:mysecretpassword@localhost/mynotes'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:dummypassword@localhost:5432/mynotes')
# 關閉不必要的追蹤，以節省系統資源
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化 SQLAlchemy，與我們的 Flask app 綁定
db = SQLAlchemy(app)


# --- 資料庫模型 (Model) ---
# 定義一個 'Note' 模型，它會對應到資料庫中的 'notes' 資料表。
class Note(db.Model):
    # __tablename__ 是可選的，如果沒寫，SQLAlchemy 會自動使用類別名稱的小寫當作表名
    __tablename__ = 'notes'
    
    # 定義欄位
    id = db.Column(db.Integer, primary_key=True) # 主鍵，會自動增長
    subject = db.Column(db.String(100), nullable=False) # 筆記的科目，不允許為空
    content = db.Column(db.Text, nullable=False) # 筆記的內容，不允許為空

    # 這個函式能幫助我們方便地將 Note 物件轉換成 Python 字典，以便轉成 JSON
    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'content': self.content
        }

# --- API 路由 (Endpoints) ---

# 路由 1: 取得所有筆記 (從資料庫讀取)
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """
    處理 GET 請求，從資料庫中查詢所有的筆記。
    """
    print("接收到 GET /api/notes 請求，從資料庫查詢筆記...")
    # 使用 Note.query.all() 取得所有筆記物件
    all_notes = Note.query.all()
    # 使用列表推導式和 to_dict() 方法將物件列表轉換成字典列表
    results = [note.to_dict() for note in all_notes]
    return jsonify(results)

# 路由 2: 新增一筆筆記 (存入資料庫)
@app.route('/api/notes', methods=['POST'])
def add_note():
    """
    處理 POST 請求，將新筆記的資料存入資料庫。
    """
    new_note_data = request.get_json(silent=True)
    if not new_note_data or 'content' not in new_note_data or 'subject' not in new_note_data:
        return jsonify({"error": "資料不完整，需要 'subject' 和 'content' 欄位"}), 400

    # 建立一個新的 Note 物件
    note = Note(
        subject=new_note_data['subject'],
        content=new_note_data['content']
    )

    # 將新物件加入到資料庫的 session 中
    db.session.add(note)
    # 提交 session，將變動寫入資料庫
    db.session.commit()

    print(f"接收到 POST /api/notes 請求，新增筆記到資料庫: {note.to_dict()}")
    # 回傳剛新增的筆記，並附上 HTTP 狀態碼 201
    return jsonify(note.to_dict()), 201

# 路由 3: 更新一筆指定的筆記
@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """
    處理 PUT 請求，根據提供的 ID 更新一筆筆記。
    """
    # 透過 ID 從資料庫中尋找筆記，如果找不到會回傳 None
    note = db.session.get(Note, note_id)
    if note is None:
        return jsonify({"error": "找不到該筆記"}), 404

    # 獲取更新資料
    update_data = request.get_json(silent=True)
    if not update_data:
        return jsonify({"error": "請求資料為空"}), 400

    # 更新筆記的 subject 和 content 欄位
    note.subject = update_data.get('subject', note.subject)
    note.content = update_data.get('content', note.content)

    # 提交變更
    db.session.commit()
    print(f"更新筆記 ID {note_id}")
    return jsonify(note.to_dict())

# 路由 4: 刪除一筆指定的筆記
@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """
    處理 DELETE 請求，根據提供的 ID 刪除一筆筆記。
    """
    note = db.session.get(Note, note_id)
    if note is None:
        return jsonify({"error": "找不到該筆記"}), 404

    # 從 session 中刪除物件並提交
    db.session.delete(note)
    db.session.commit()
    
    print(f"刪除筆記 ID {note_id}")
    # 回傳一個空的成功回應
    return '', 204

# --- 主程式進入點 ---
if __name__ == '__main__':
    # 透過 with app.app_context()，確保應用程式的上下文被正確設定
    with app.app_context():
        # 這行指令會根據你定義的模型，在資料庫中建立對應的資料表。
        # 如果資料表已經存在，它不會重複建立。
        print("正在檢查並建立資料庫表格...")
        db.create_all()
        print("資料庫表格已就緒！")

    # 啟動 Flask 應用程式
    app.run(host='0.0.0.0', port=8080, debug=True)
