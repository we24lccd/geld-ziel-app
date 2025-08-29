from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from config import UPLOAD_FOLDER
from utils import allowed_file, format_currency
from models import read_data, write_data, enrich_goal
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    data = read_data()
    goals = [enrich_goal(g) for g in data['goals']]
    return render_template('index.html', goals=goals)

@app.route('/goal/<int:goal_id>')
def get_goal(goal_id):
    data = read_data()
    try:
        goal = enrich_goal(data['goals'][goal_id])
        return jsonify(goal)
    except IndexError:
        return jsonify({"error": "Không tìm thấy mục tiêu."}), 404

@app.route('/add_goal', methods=['POST'])
def add_goal():
    req = request.json
    description = req.get('description')
    amount = req.get('amount')
    deadline = req.get('deadline')

    if not description or not amount or amount <= 0:
        return jsonify({"error": "Thông tin mục tiêu không hợp lệ"}), 400

    data = read_data()
    data['goals'].append({
        "description": description,
        "amount": amount,
        "deadline": deadline,
        "deposits": []
    })
    write_data(data)
    return jsonify({"message": "Đã thêm mục tiêu mới!"})

@app.route('/deposit/<int:goal_id>', methods=['POST'])
def deposit(goal_id):
    amount = None
    note = ""
    if request.is_json:
        amount = request.json.get('amount')
        note = request.json.get('note', "")
    else:
        amount = request.form.get('amount', type=float)
        note = request.form.get('note', "")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = None

    if amount is None or amount <= 0:
        return jsonify({"error": "Số tiền không hợp lệ"}), 400

    data = read_data()
    if goal_id < 0 or goal_id >= len(data['goals']):
        return jsonify({"error": "ID mục tiêu không hợp lệ"}), 404

    from datetime import datetime, timedelta
    vn_time = datetime.utcnow() + timedelta(hours=7)
    new_deposit = {
        "amount": amount,
        "timestamp": vn_time.strftime('%Y-%m-%d %H:%M:%S'),
        "note": note
    }
    data['goals'][goal_id]['deposits'].append(new_deposit)
    write_data(data)

    updated_goal = enrich_goal(data['goals'][goal_id])

    return jsonify({
        "message": f"Đã thêm khoản tích lũy {format_currency(amount)} VND!",
        "goal": updated_goal
    }), 200

@app.route('/deposit/<int:goal_id>/<int:deposit_index>', methods=['DELETE'])
def delete_deposit(goal_id, deposit_index):
    data = read_data()
    try:
        goal = data['goals'][goal_id]
        deleted = goal['deposits'].pop(deposit_index)
        write_data(data)
        return jsonify({"message": f"Đã xoá khoản tích lũy {format_currency(deleted['amount'])} VND"})
    except (IndexError, KeyError):
        return jsonify({"error": "Không tìm thấy khoản tích lũy"}), 404

@app.route('/goal/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    data = read_data()
    try:
        deleted_goal = data['goals'].pop(goal_id)
        write_data(data)
        return jsonify({"message": f"Đã xóa mục tiêu '{deleted_goal['description']}' thành công."})
    except (IndexError, KeyError):
        return jsonify({"error": "Không tìm thấy mục tiêu."}), 404

@app.route('/reset', methods=['POST'])
def reset():
    write_data({"goals": []})
    return jsonify({"message": "Đã reset app về trạng thái ban đầu."})

@app.route('/upload_image/<int:goal_id>', methods=['POST'])
def upload_image(goal_id):
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"goal_{goal_id}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        data = read_data()
        if 0 <= goal_id < len(data['goals']):
            data['goals'][goal_id]['image'] = filename
            write_data(data)

        return jsonify({"message": "Ảnh đã được cập nhật"})
    return jsonify({"error": "Invalid file"}), 400

@app.route('/update_goal/<int:goal_id>', methods=['POST'])
def update_goal(goal_id):
    data = read_data()
    if goal_id < 0 or goal_id >= len(data['goals']):
        return jsonify({"error": "ID mục tiêu không hợp lệ"}), 404

    req = request.json
    new_desc = req.get('description', '').strip()
    if not new_desc:
        return jsonify({"error": "Mô tả không được để trống."}), 400

    data['goals'][goal_id]['description'] = new_desc
    write_data(data)
    return jsonify({"message": "Đã cập nhật tên mục tiêu."})

@app.route('/deposit/<int:goal_id>/<int:deposit_index>/note', methods=['POST'])
def update_deposit_note(goal_id, deposit_index):
    data = read_data()
    try:
        note = request.json.get('note', '')
        data['goals'][goal_id]['deposits'][deposit_index]['note'] = note
        write_data(data)
        return jsonify({"message": "Đã cập nhật ghi chú!"})
    except (IndexError, KeyError):
        return jsonify({"error": "Không tìm thấy khoản tích lũy"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)