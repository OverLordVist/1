from config import bot
from database import db
from telebot import types
import difflib as df
import random

main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add('Быстрый поиск ответов')
main_keyboard.add('Вопросы к экзамену', 'Термины', 'Проверь себя')
main_keyboard.add('Дополнительная информация')


def create_user(message):
    user_id = message.from_user.id
    db.create_user(user_id, message.text)
    bot.send_message(user_id, 'Удачи на блядском экзамене!', reply_markup=main_keyboard)


def send_answers_list(message):
    user_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for answer in db.questions_dict.keys():
        name = f'{answer}. {db.questions_dict[answer]["name"]}'
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=str(answer)))
    bot.send_message(user_id, 'Выберите вопрос: ', reply_markup=keyboard)


def send_concepts_list(message):
    user_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for concept in db.concepts_dict.keys():
        name = f'{concept}. {db.concepts_dict[concept]["name"]}'
        call_str = 'concept ' + str(concept)
        keyboard.add(types.InlineKeyboardButton(text=name, callback_data=call_str))
    bot.send_message(user_id, 'Выберите нужный Вам термин:', reply_markup=keyboard)


def start_questions_test(message):
    user_id = message.chat.id
    number_question = random.randint(1, 46)
    send_str = f'*Ответьте на вопрос: *\n {db.questions_dict[number_question]["name"]}'
    call_str = 'next_q ' + str(number_question)
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Просмотреть ответ',
                                                                                      callback_data=call_str))
    bot.send_message(user_id, send_str, parse_mode='Markdown', reply_markup=keyboard)


def start_concepts_test(message):
    user_id = message.chat.id
    number_concept = random.randint(1, 80)
    send_str = f'*Ответьте на вопрос: *\n {db.concepts_dict[number_concept]["name"]}'
    call_str = 'next_c ' + str(number_concept)
    keyboard = types.InlineKeyboardMarkup(row_width=1).add(types.InlineKeyboardButton(text='Просмотреть ответ',
                                                                                      callback_data=call_str))
    bot.send_message(user_id, send_str, parse_mode='Markdown', reply_markup=keyboard)


def get_answer_find(message):
    questions_name = []
    questions_calls = {}
    user_id = message.from_user.id
    n = 4
    cutoff = 0.3
    for i in db.questions_dict.keys():
        questions_name.append(db.questions_dict[i]['name'])
        questions_calls[db.questions_dict[i]['name']] = str(i)
    result = df.get_close_matches(message.text, questions_name, n, cutoff)
    if not result:
        bot.send_message(user_id, 'Такого вопроса нет. Пропишите еще раз:')
        bot.register_next_step_handler(message, get_answer_find)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        if len(result) > 1:
            for i in range(1, len(result)):
                keyboard.add(types.InlineKeyboardButton(text=result[i], callback_data=questions_calls[result[i]]))
            bot.send_message(user_id, 'Помимо отправленного ответа, есть еще 3 схожих по названию вопроса:',
                             reply_markup=keyboard)
            bot.send_document(user_id, db.questions_dict[int(questions_calls[result[0]])]['file_id'],
                              caption=db.questions_dict[int(questions_calls[result[0]])]['name'])
        else:
            bot.send_message(user_id, 'Это был единственный вопрос, который подходил по названию в списке.')
            bot.send_document(user_id, db.questions_dict[int(questions_calls[result[0]])]['file_id'],
                              caption=db.questions_dict[int(questions_calls[result[0]])]['name'])


def get_concept_find(message):
    concepts_name = []
    concepts_calls = {}
    user_id = message.from_user.id
    n = 4
    cutoff = 0.3
    for i in db.concepts_dict.keys():
        concepts_name.append(db.concepts_dict[i]['name'])
        concepts_calls[db.concepts_dict[i]['name']] = str(i)
    result = df.get_close_matches(message.text, concepts_name, n, cutoff)
    if not result:
        bot.send_message(user_id, 'Такого термина нет. Пропишите еще раз:')
        bot.register_next_step_handler(message, get_concept_find)
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        if len(result) > 1:
            for i in range(1, len(result)):
                call_str = 'concept ' + concepts_calls[result[i]]
                keyboard.add(types.InlineKeyboardButton(text=result[i], callback_data=call_str))
            bot.send_message(user_id, 'Помимо отправленного ответа, есть еще несколько схожих по названию термина:',
                             reply_markup=keyboard)
            bot.send_message(user_id, db.concepts_dict[int(concepts_calls[result[0]])]['description'])
        else:
            bot.send_message(user_id, 'Это был единственный термин, который подходил по названию в списке.')
            send_str = f'*{db.concepts_dict[int(concepts_calls[result[0]])]["name"]}*\n' \
                       f'{db.concepts_dict[int(concepts_calls[result[0]])]["description"]}'
            bot.send_message(user_id, send_str)