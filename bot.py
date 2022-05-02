import os
import telebot
from bs4 import BeautifulSoup
import youtube_dl
import requests
import ytm

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

def download(title, video_url):
    ydl_opts = {
        'outtmpl': '{}.%(ext)s'.format(title),
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return {
        'audio': open(title + '.mp3', 'rb'),
        'title': title,
    }

bot = telebot.TeleBot(token=token)

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, 'Heil og sæl\nYour music name is my command')

@bot.message_handler(func=lambda message: True)
def music(message):
	link, name, artist = search_youtube(message.text)
	if link is None:
		bot.send_message(message.chat.id, 'No results found')
		return
	bot.reply_to(message, 'Wait for it...')
	title = f"{artist} - {name}"
	music_dict = download(title, link)
	bot.send_audio(message.chat.id, music_dict['audio'], title=music_dict['title'])
	os.remove(title + '.mp3')

bot.infinity_polling()