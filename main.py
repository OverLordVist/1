from config import bot, constant_files_ids
from database import db
from app import create_user, main_keyboard, send_answers_list, get_answer_find, send_concepts_list, get_concept_find, \
    start_questions_test, start_concepts_test
from telebot import types


@bot.message_handler(commands=['start'])
def get_start_message(message):
    user_id = message.from_user.id
    if not db.check_db(user_id):
        bot.send_message(user_id, 'Введите имя и фамилию:')
        bot.register_next_step_handler(message, create_user)
    else:
        bot.send_message(user_id, 'Нам пизда))0', reply_markup=main_keyboard)


@bot.message_handler(content_types=['text', 'document'])
def get_menu_action(message):
    user_id = message.from_user.id
    action = message.text
    if action == 'Вопросы к экзамену':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='Все вопросы одним файлом', callback_data='all_answers'),
                     types.InlineKeyboardButton(text='Выбрать вопросы', callback_data='ans_list'))
        bot.send_message(user_id, 'Тебе все сразу или конкретный вопрос?', reply_markup=keyboard)
    elif action == 'Быстрый поиск ответов':
        bot.send_message(user_id, 'Напишите вопрос из билета (можно допускать ошибки): ')
        bot.register_next_step_handler(message, get_answer_find)
    elif action == 'Термины':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='Термины одним файлом', callback_data='all_concepts'),
                     types.InlineKeyboardButton(text='Список терминов', callback_data='concepts_list'),
                     types.InlineKeyboardButton(text='Поиск терминов по названию', callback_data='find_concept'))
        bot.send_message(user_id, 'Выберите удобный поиск терминов:', reply_markup=keyboard)
    elif action == 'Проверь себя':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='Вопросы', callback_data='test_questions'),
                     types.InlineKeyboardButton(text='Термины', callback_data='test_concepts'))
        bot.send_message(user_id, 'Ваша задача - самостоятельно отвечать на вопросы или давать понятия терминам. Вам '
                                  'отсылается вопрос или термин, далее самостоятельно даете ответ (не боту, ему вообще'
                                  ' похуй на твою философию), и проверяете правильный ответ (там на кнопку нажмете).',
                         reply_markup=keyboard)
    elif action == 'Дополнительная информация':
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(text='Ответы на вопросы (физлиб)', callback_data='physlibanswers'),
                     types.InlineKeyboardButton(text='Шпоры (физлиб)', callback_data='shpori'),
                     types.InlineKeyboardButton(text='Электронный конспект', callback_data='kons'))
        bot.send_message(user_id, 'Дополнительный материал:', reply_markup=keyboard)
    else:
        print(message.document.file_id)


@bot.callback_query_handler(func=lambda call: True)
def get_callback_data(call):
    user_id = call.message.chat.id
    large_call_data = call.data.split(' ')
    if call.data == 'all_answers':
        bot.send_document(user_id, constant_files_ids['all answers'])
    elif call.data == 'ans_list':
        send_answers_list(call.message)
    elif call.data.isdigit() and int(call.data) in db.questions_dict.keys():
        bot.send_document(user_id, db.questions_dict[int(call.data)]['file_id'])
    elif call.data == 'all_concepts':
        bot.send_document(user_id, constant_files_ids['all concepts'])
    elif call.data == 'concepts_list':
        send_concepts_list(call.message)
    elif call.data == 'find_concept':
        bot.send_message(user_id, 'Введите название термина:')
        bot.register_next_step_handler(call.message, get_concept_find)
    elif call.data == 'test_questions':
        start_questions_test(call.message)
    elif call.data == 'test_concepts':
        start_concepts_test(call.message)
    elif call.data == 'physlibanswers':
        bot.send_document(user_id, constant_files_ids['ответы с физлиба'])
    elif call.data == 'shpori':
        bot.send_document(user_id, constant_files_ids['шпоры'])
    elif call.data == 'kons':
        bot.send_document(user_id, constant_files_ids['конспект'])
    elif large_call_data[0] == 'next_q':
        bot.send_document(user_id, db.c[int(large_call_data[1])]['file_id'], caption='Ответ в файле.')
        start_concepts_test(call.message)
    elif large_call_data[0] == 'next_c':
        send_str = f'*{db.concepts_dict[int(large_call_data[1])]["name"]}*\n' \
                   f'{db.concepts_dict[int(large_call_data[1])]["description"]}'
        bot.send_message(user_id, send_str, parse_mode='Markdown')
        start_questions_test(call.message)
    elif large_call_data[0] == 'concept':
        send_str = f'*{db.concepts_dict[int(large_call_data[1])]["name"]}*\n' \
                   f'{db.concepts_dict[int(large_call_data[1])]["description"]}'
        bot.send_message(user_id, send_str, parse_mode='Markdown')


if __name__ == '__main__':
    bot.infinity_polling()
