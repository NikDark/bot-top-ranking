import telebot
import os
import time

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from work_music import get_links, download_music_link

bot = telebot.TeleBot("1377360563:AAH4U7RFBVky5ttCrSMSTObEAFxOPOnNsDA", parse_mode=None)

CHAT_ID = None
COUNT_MUSIC = 20
ROW_WIDTH = 5
MUSIC_POS = [str(pos) for pos in range(COUNT_MUSIC)]
MARKS = [0 for _ in range(COUNT_MUSIC)]
ADMINS_ID = [359862454]
VOTED_USERS = []
TIME_FOR_VOTE = 10 # in seconds
NUM_PER_PAGE = 3
PAGE = 0
TITLES = []
POOL_CREATED = False
MAX_PAGE = COUNT_MUSIC//NUM_PER_PAGE

ZERO = '\U00000030\U000020E3'
ONE = '\U00000031\U000020E3'
TWO = '\U00000032\U000020E3'
THREE = '\U00000033\U000020E3'
FOUR = '\U00000034\U000020E3'
FIVE = '\U00000035\U000020E3'
SIX = '\U00000036\U000020E3'
SEVEN = '\U00000037\U000020E3'
EIGHT = '\U00000038\U000020E3'
NINE = '\U00000039\U000020E3'

NUMBERS = [ZERO,ONE,TWO,THREE,FOUR,FIVE,SIX,SEVEN,EIGHT,NINE]

def gen_markup(page_number):
	markup = InlineKeyboardMarkup()
	markup.row_width = ROW_WIDTH
	page_button = []
	if page_number != 0:
		page_button.append(InlineKeyboardButton(f'<<',callback_data='Pred-page'))
	from_num = NUM_PER_PAGE*page_number
	if NUM_PER_PAGE+NUM_PER_PAGE*page_number > COUNT_MUSIC:
		to_num = COUNT_MUSIC
	else:
		to_num = NUM_PER_PAGE+NUM_PER_PAGE*page_number
	print(from_num,to_num)
	button_list = [InlineKeyboardButton(f'{index+1 if index >= 9 else NUMBERS[index+1]} - {MARKS[index]}',callback_data=MUSIC_POS[index]) for index in range(COUNT_MUSIC)][from_num:to_num]
	markup.add(*button_list)
	if page_number != MAX_PAGE:
		page_button.append(InlineKeyboardButton(f'>>',callback_data='Next-page'))
	markup.add(*page_button)
	return markup

@bot.callback_query_handler(func=lambda call: True)
def get_callback_query(call):
	global PAGE
	
	if call.data == 'Pred-page' and PAGE > 0:
		PAGE-=1
	elif call.data == 'Next-page' and PAGE < MAX_PAGE :
		PAGE+=1
	elif PAGE == 0:
		bot.answer_callback_query(call.id, f"No pred_page")
	elif PAGE == MAX_PAGE:
		bot.answer_callback_query(call.id, f"No next_page")
	try:
		if (call.from_user.id, call.data) not in VOTED_USERS:
			MARKS[int(call.data)] += 1
			VOTED_USERS.append((call.from_user.id, call.data))
		else:
			MARKS[int(call.data)] -= 1
			VOTED_USERS.pop(VOTED_USERS.index((call.from_user.id, call.data)))
	except ValueError:
		pass
	bot.answer_callback_query(call.id, f"Answer is {call.data}")
	update_pool(PAGE,call.message.chat.id, call.message.message_id)
	bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=gen_markup(PAGE))
	

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, r"Use /pool for starting pool of music")

@bot.message_handler(commands=['help'])
def start(message):
	bot.send_message(message.chat.id, r"Use /pool for starting pool of music")

def receive_top_music(chat_id,links,message):
	# bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
	# bot.edit_message_reply_markup(, reply_markup=None)
	index_max = 0
	if not VOTED_USERS:
		bot.send_message(chat_id, "No one voted\nLoading the first song")
	else:
		max_elem = max(MARKS)
		index_max = MARKS.index(max_elem)
		bot.send_message(chat_id,f"According to the results of voting, the winning composition is ... 🥁'Bam'🥁'Bam'🥁'Bam'🥁'Bam'")

	download_music_link(links[index_max],index_max)
	audio = open(f'{index_max}.mp3','rb')
	bot.send_audio(chat_id,audio)
	os.remove(f'{index_max}.mp3')

def pool_over():
	global PAGE
	global LINKS
	global TITLES
	for index in range(COUNT_MUSIC):
		MARKS[index] = 0
		VOTED_USERS.clear()
	PAGE = 0
	LINKS = []
	TITLES = []
	POOL_CREATED = False
	

@bot.message_handler(commands=['pool'])
def create_pool(message):
	if POOL_CREATED:
		bot.send_message(message.chat.id,'Pool was created')
		return
	# ADMINS_ID = [admin.user.id for admin in bot.get_chat_administrators(message.chat.id)]
	global TITLES

	# if message.from_user.id in ADMINS_ID:
	if True:
		links, TITLES = get_links(COUNT_MUSIC)
		music_pool = f"""
1. {TITLES[0]}
2. {TITLES[1]}
3. {TITLES[2]}
		"""
		bot.send_message(message.chat.id, music_pool, reply_markup=gen_markup(PAGE))
		time.sleep(TIME_FOR_VOTE)
		receive_top_music(message.chat.id,links,message)
		pool_over()
	else:
		bot.send_message(message.chat.id, r"You don't have permission")

def update_pool(page,chat_id,message_id):
	global TITLES
	from_num = NUM_PER_PAGE*page
	if NUM_PER_PAGE+NUM_PER_PAGE*page > COUNT_MUSIC:
		to_num = COUNT_MUSIC
	else:
		to_num = NUM_PER_PAGE+NUM_PER_PAGE*page
	music_pool = [f'{index+1} - {TITLES[index-1]}' for index in range(from_num,to_num)]
	text = '\n'.join(music_pool)
	bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=text)
	