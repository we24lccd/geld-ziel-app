from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime, date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
DATA_FILE = 'data.json'


def read_data():
    if not os.path.exists(DATA_FILE):
        return {"goals": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def format_currency(amount):
    return f"{amount:,.0f}".replace(",", ".")


def number_to_words(n):
    from num2words import num2words
    if n <= 0:
        return "không"
    try:
        return num2words(n, lang='vi')
    except Exception:
        return "không xác định"


def capitalize_first(s):
    return s[0].upper() + s[1:] if s else s


def enrich_goal(goal):
    goal['description'] = capitalize_first(goal['description'].strip())

    total = sum(d['amount'] for d in goal['deposits'])
    remaining = goal['amount'] - total
    goal['total_saved'] = total
    goal['remaining'] = remaining
    goal['completed'] = total >= goal['amount']

    if goal['completed']:
        goal['daily_needed'] = 0
        goal['daily_needed_fmt'] = "0 (Không cần tích lũy)"
        goal['progress_percent'] = 100
        goal['completion_message'] = "🎉 Chúc mừng đã hoàn thành mục tiêu!"
    else:
        goal['progress_percent'] = min((total / goal['amount']) * 100, 100)
        goal['daily_needed'] = 0
        if goal.get('deadline'):
            days_left = (date.fromisoformat(goal['deadline']) - date.today()).days
            if days_left > 0:
                goal['daily_needed'] = round(remaining / days_left, 2)

        if goal['daily_needed']:
            daily_needed_int = int(round(goal['daily_needed']))
            daily_needed_words = capitalize_first(number_to_words(daily_needed_int)) if daily_needed_int > 0 else "Không cần tích lũy"
            goal['daily_needed_fmt'] = f"{format_currency(goal['daily_needed'])} ({daily_needed_words})"
        else:
            goal['daily_needed_fmt'] = "0 (Không cần tích lũy)"

    goal['amount_fmt'] = f"{format_currency(goal['amount'])} ({capitalize_first(number_to_words(goal['amount']))})"
    goal['total_saved_fmt'] = f"{format_currency(total)} ({capitalize_first(number_to_words(total))})"

    for d in goal['deposits']:
        d['amount_fmt'] = f"{format_currency(d['amount'])}"
        percent = (d['amount'] / goal['amount']) * 100 if goal['amount'] else 0
        d['percent'] = round(percent, 1)
        d['amount_words'] = capitalize_first(number_to_words(d['amount']))

    return goal

@app.route('/')
def index():
    data = read_data()
    goals = [enrich_goal(g) for g in data['goals']]
    return render_template('index.html', goals=goals)


@app.route('/goal/<int:goal_id>')
def get_goal(goal_id):
    """API lấy dữ liệu 1 mục tiêu"""
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
    # Lấy số tiền từ JSON hoặc form
    amount = None
    if request.is_json:
        amount = request.json.get('amount')
    else:
        amount = request.form.get('amount', type=float)

    # Kiểm tra số tiền hợp lệ
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = None

    if amount is None or amount <= 0:
        return jsonify({"error": "Số tiền không hợp lệ"}), 400

    # Đọc dữ liệu
    data = read_data()
    if goal_id < 0 or goal_id >= len(data['goals']):
        return jsonify({"error": "ID mục tiêu không hợp lệ"}), 404

    # Thêm khoản tích lũy
    new_deposit = {
        "amount": amount,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    data['goals'][goal_id]['deposits'].append(new_deposit)
    write_data(data)

    # Enrich dữ liệu trả về
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)