import os
import telebot
from bs4 import BeautifulSoup
import youtube_dl
import requests
import ytm
import eyed3

token = os.getenv('TOKEN')
if token is None:
	print('No token found')
	exit(1)

yt_api = ytm.YouTubeMusic()

def search_youtube(text):
	songs = yt_api.search_songs(text)
	if len(songs['items']) == 0:
		return None, None, None
	song = songs['items'][0]
	return f"https://youtube.com/watch?v={song['id']}", song['name'], song['artists'][0]['name']

def download(title, artist, video_url):
	filename = f"{title} - {artist}"

	ydl_opts = {
		'outtmpl': '{}.%(ext)s'.format(filename),
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([video_url])

	return filename

def set_tags(filename, title, artist):
	audio = eyed3.load(filename + '.mp3')
	audio.tag.artist = artist
	audio.tag.title = title
	audio.tag.save()

bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Heil og sæl\nYour music name is my command')

@bot.message_handler(func=lambda message: True)
def music(message):
	link, title, artist = search_youtube(message.text)
	if link is None:
		bot.send_message(message.chat.id, 'No results found')
		return
	bot.reply_to(message, 'Wait for it...')
	filename = download(title, artist, link)
	set_tags(filename, title, artist)
	with open(filename + '.mp3', 'rb') as f:
		bot.send_audio(message.chat.id, f)
	os.remove(filename + '.mp3')

bot.infinity_polling()