import os
import json
from datetime import date
from config import DATA_FILE
from utils import format_currency, number_to_words, capitalize_first

def read_data():
    if not os.path.exists(DATA_FILE):
        return {"goals": []}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def enrich_goal(goal):
    goal['description'] = capitalize_first(goal['description'].strip())

    total = sum(d['amount'] for d in goal['deposits'])
    remaining = goal['amount'] - total
    goal['total_saved'] = total
    goal['remaining'] = remaining
    goal['completed'] = total >= goal['amount']

    if goal['completed']:
        goal['daily_needed'] = 0
        goal['daily_needed_fmt'] = "0 (Đã hoàn thành)"
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
            daily_needed_words = capitalize_first(number_to_words(daily_needed_int)) if daily_needed_int > 0 else "Đã hoàn thành"
            goal['daily_needed_fmt'] = f"{format_currency(goal['daily_needed'])} ({daily_needed_words})"
        else:
            goal['daily_needed_fmt'] = "0 (Đã hoàn thành)"

    goal['amount_fmt'] = f"{format_currency(goal['amount'])} ({capitalize_first(number_to_words(goal['amount']))})"
    goal['total_saved_fmt'] = f"{format_currency(total)} ({capitalize_first(number_to_words(total))})"

    for d in goal['deposits']:
        d['amount_fmt'] = f"{format_currency(d['amount'])}"
        percent = (d['amount'] / goal['amount']) * 100 if goal['amount'] else 0
        d['percent'] = round(percent, 1)
        d['amount_words'] = capitalize_first(number_to_words(d['amount']))

    return goal