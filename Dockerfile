FROM python:alpine

WORKDIR /bot

RUN apk add --no-cache ffmpeg git

COPY . .

RUN pip install -r requirements.txt

RUN git clone https://github.com/tombulled/python-youtube-music.git && cd python-youtube-music && pip install .

CMD ["python3", "bot.py"]
