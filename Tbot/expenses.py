import datetime
import pytz

from typing import List, NamedTuple, Optional

import db

CATEGORIES = ['дом', 'ресторан', 'такси', 'кино']


class Message(NamedTuple):
    """Структура полученного уведомления"""
    amount: int
    category: str


class Expense(NamedTuple):
    """Структура"""
    id: Optional[int]
    amount: int
    category: str


def add_expense(raw_message: str) -> Expense:
    parsed_message = _parse_message(raw_message)

    today_datetime = _get_current_datetime()
    created = today_datetime.strftime("%Y-%m-%d %H:%M:%S")

    db.insert("expense", {
        "amount": parsed_message.amount,
        "created": created,
        "category": parsed_message.category,
    })
    return Expense(id=None, amount=parsed_message.amount, category=parsed_message.category)

def get_today_statistics() -> str:
    cursor = db.get_cursor()
    cursor.execute("select sum(amount)"
                   "from expense where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня нет затрат"

    return (f"Затраты за сегодня: \n"
            f"Всего - {result[0]} руб.")


def get_month_statistics() -> str:
    now = _get_current_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'")
    result = cursor.fetchone()
    if not result[0]:
        return "В этом месяце нет затрат"

    return (f"Затраты за месяц: \n"
            f"Всего - {result[0]} руб.")

def last() -> List[Expense]:
    cursor = db.get_cursor()
    cursor.execute(
        "select expense.id, expense.amount, expense.category "
        "from expense "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category=row[2]) for row in rows]
    return last_expenses

def delete_expense(row_id: int) -> None:
    db.delete("expense", row_id)

def _parse_message(raw_message: str) -> Message:
    amount, category = raw_message.split(maxsplit=1)
    if category not in CATEGORIES:
        raise Exception(f"Категории '{category}' нет ")

    return Message(amount=amount, category=category)

def _get_current_datetime():
    tz = pytz.timezone("Europe/Moscow")
    today_datetime = datetime.datetime.now(tz)
    return today_datetime