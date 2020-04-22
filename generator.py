from feedgen.feed import FeedGenerator
from mutagen.mp3 import MP3
from string import Template
import json
import os
import datetime
import markdown2

class DeltaTemplate(Template):
    delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = '{:02d}'.format(hours)
    d["M"] = '{:02d}'.format(minutes)
    d["S"] = '{:02d}'.format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

episodedir = 'episodes'

with open('show.json', encoding="utf-8") as f1:
    showinfo = json.load(f1)

fg = FeedGenerator()

hosthead = showinfo["host-address"]
fg.title(showinfo["title"])
fg.author(showinfo["author"])
fg.logo(hosthead + showinfo["logo"]["url"])
fg.subtitle(showinfo["description"])
fg.link( href=showinfo["link"], rel='self' )
fg.language(showinfo["language"])

fg.load_extension('podcast')

fg.podcast.itunes_category(showinfo["itunes-category"]["cat1"], showinfo["itunes-category"]["cat2"])
fg.podcast.itunes_owner(showinfo["author"]["name"], showinfo["author"]["email"])
fg.podcast.itunes_image(hosthead + showinfo["logo"]["url"])

for directory, subdirectories, files in os.walk(episodedir):
    for file in files:
        if file.endswith('.json'):
            filename = episodedir + "/" + file
            with open(filename) as f2:
                episodeinfo = json.load(f2)
                audio = MP3(episodeinfo["audio"]["url"])
                filelength = os.path.getsize(episodeinfo["audio"]["url"])
                duration = strfdelta(datetime.timedelta(seconds=audio.info.length), '%H:%M:%S')

                a = str(episodeinfo["shownote"])
                snhtml = markdown2.markdown(a, extras=["cuddled-lists"])

                fe = fg.add_entry()
                fe.title(episodeinfo["title"])
                fe.description(episodeinfo["description"])
                fe.enclosure(hosthead + episodeinfo["audio"]["url"], str(round(filelength)), episodeinfo["audio"]["type"])
                fe.content(snhtml, type="CDATA")
                fe.podcast.itunes_image(episodeinfo["image"])
                fe.podcast.itunes_duration(duration)
                fe.podcast.itunes_subtitle(episodeinfo["description"])
                fe.podcast.itunes_author(showinfo["author"]["name"])

fg.rss_str(pretty=True)
fg.rss_file('podcast.xml')
