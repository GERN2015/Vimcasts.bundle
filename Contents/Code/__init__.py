import htmlentitydefs
import re
from datetime import datetime
from email.utils import parsedate

VIMCASTS_FEED_URL      = 'http://vimcasts.org/episodes.json'
VIMCASTS_ICON          = 'icon-default.png'
VIMCASTS_ART           = 'art-default.jpg'

###############################################################################
def Start():
    Plugin.AddPrefixHandler("/video/vimcasts", VideoMenu, L('vimcasts'), VIMCASTS_ICON, VIMCASTS_ART)
    Plugin.AddViewGroup("Details", viewMode = "InfoList", mediaType = "items")

    ObjectContainer.title1 = L('vimcasts')
    ObjectContainer.view_group = 'Details'
    ObjectContainer.art = R(VIMCASTS_ART)

    DirectoryObject.thumb = R(VIMCASTS_ICON)
    DirectoryObject.art = R(VIMCASTS_ART)
    VideoClipObject.thumb = R(VIMCASTS_ICON)
    VideoClipObject.art = R(VIMCASTS_ART)

    HTTP.CacheTime        = CACHE_1HOUR

def VideoMenu():
    oc = ObjectContainer()
    episodes = JSON.ObjectFromURL(VIMCASTS_FEED_URL)['episodes']
    episodes.reverse()  # Newest first
    for episode in episodes:
        try:
            url     = episode['url']
            title   = F('episode', episode['episode_number'], episode['title'])
            date    = parsedate(episode['published_at'])
            date    = datetime(*date[:6])
            summary = dehtmlize(episode['abstract'].strip())
            thumb   = episode['poster']


            oc.add(VideoClipObject(
                url = url,
                title = title,
                summary = summary,
                thumb = thumb,
                originally_available_at = date))

        except AttributeError:
            Log("Something odd with episode, skipping: %s" %
                    episode, debugOnly=False)
    return oc

##
# Removes HTML tags from a text string and converts character entities.
# Adapted from:
# http://effbot.org/zone/re-sub.htm#strip-html
#
# @param text The HTML source.
# @return The plain text.  If the HTML source contains non-ASCII
#     entities or character references, this is a Unicode string.
def dehtmlize(text):
    def convert_entities(m):
        text = m.group(0)
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return String.StripTags(re.sub("&#?\w+;", convert_entities, text))