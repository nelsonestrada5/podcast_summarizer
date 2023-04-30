# Updates
from pydub import AudioSegment

podcast = AudioSegment.from_file("/Users/nelsonestrada/Downloads/estoy_escribiendo_un_libro.m4a")

# PyDub handles time in milliseconds
ten_minutes = 10 * 60 * 1000
one_minute = 10 * 60 * 1000


first_minute = podcast[:one_minute]

first_minute.export("good_morning_10.mp3", format="mp3")
