from aiogram import Bot, Dispatcher, types, executor

import expenses

TOKEN = "5923531527:AAF5o_eT4c2bBx0yHlm5FzrmKsa6p8sMkL0"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Привет, это мой бот телеграм\n\n"
        "Добавить расходы: 300 продукты\n"
        "Отредактировать список доступных категорий: /categories\n"
        "Статистика затрат за день: /today\n"
        "Статистика затрат за месяц: /month\n"
        "Посмотрите последние расходы: /expenses\n"
    )

@dp.message_handler(lambda message: message.text.startswith('/del'))
async def start(message: types.Message):
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалено!"
    await message.answer(answer_message)

@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    answer_message = "Список категорий: \n\n * " + ("\n * ".join(expenses.CATEGORIES))
    await message.answer(answer_message)

@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)

@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)

@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("Затрат нет")
        return

    last_expenses_rows = [
        f"{expense.amount} руб. на {expense.category} - жми /del{expense.id} для удаления"
        for expense in last_expenses]
    answer_message = "Осталось затрат:\n\n* " + "\n\n* ".join(last_expenses_rows)
    await message.answer(answer_message)

@dp.message_handler()
async def add_expense(message: types.Message):
    try:
        expense = expenses.add_expense(message.text)
    except Exception as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлено затрат {expense.amount} руб на {expense.category}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)

if __name__ == '__main__':
    print("Ready")
    executor.start_polling(dp, skip_updates=True)
