# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
# Copyright © 2015-2021 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

'''Build the message'''

# standard libraires imports
import logging

# external liraries imports
from bs4 import BeautifulSoup

# app libraries imports
from feed2toot.addtags import AddTags
from feed2toot.removeduplicates import RemoveDuplicates
from feed2toot.tootpost import TootPost

def custom_format(entrytosend):
    # assume tweetformat is: {title} {link} {summary}
    
    ship_tags = []
    
    if 'title' in entrytosend:
        title = entrytosend['title']
    else: title = ''
    
    if 'summary' in entrytosend:
        summary = entrytosend['summary']
        soup = BeautifulSoup(summary, 'lxml')
        para = soup.find_all('p')
        author = para[0].get_text()  # by Anon
        
        # At first I thought the last <p> tag contains stats (e.g., words, chapters, and language).
        # there can be another <p> tag of "Series" below stats para
        # so not the last <p>
        
        # need to find where the stats <p> actually is
        pos = 0
        for idx, p in enumerate(para):
            text = p.get_text()
            if "Words:" in text and "Chapters" in text:
                pos = idx
                break
            
        # Summary can contain multiple paragraphs (usually no '\n' used in <p> tag, use <br> instead)
        # there might be formats like "\n <i> italic text <\i> \n", so just strip 'em
        summ = '\n'.join([i.get_text().strip('\n') for i in para[1 : pos]])        
        stats = para[pos].get_text()
        
        tags_li = soup.find_all('li')
        for tag_li in tags_li:
            plain_text = tag_li.get_text()
            if 'Relationships' in plain_text:
                ship_tags = [x.get_text() for x in tag_li.find_all('a')]
                break
    else: summary = ''
    
    if 'link' in entrytosend:
        link = entrytosend['link'] + '\n'
    else: link =''
        
    if 'published' in entrytosend:
        # timestamp format: 2022-06-10T06:13:02Z
        published = entrytosend['published'].replace('T', ' ').replace('Z', ' UTC') + '\n'
    else: published = ''
        
    tweetwithnotag = title + ' - ' + author + '\n' + published + link + '\n'
    tweetwithnotag += "Summary:\n" + summ + '\n\n' + stats + '\n'
    if len(ship_tags) > 0:
        tweetwithnotag += "Relationships: " + ', '.join(ship_tags)
    
    return tweetwithnotag


def build_message(entrytosend, tweetformat, rss, tootmaxlen, notagsintoot):
    '''populate the rss dict with the new entry'''
    #tweetwithnotag = tweetformat.format(**entrytosend)  ## **传参，dict形式
    logging.debug(entrytosend)
    tweetwithnotag = custom_format(entrytosend)
    # replace line breaks
    tootwithlinebreaks = tweetwithnotag.replace('\\n', '\n')
    # remove duplicates from the final tweet
    dedup = RemoveDuplicates(tootwithlinebreaks)
    # only add tags if user wants to
    if not notagsintoot:
        # only append hashtags if they exist
        # remove last tags if tweet too long
        if 'hashtags' in rss:
            addtag = AddTags(dedup.finaltweet, rss['hashtags'])
            finaltweet = addtag.finaltweet
        else:
            finaltweet = dedup.finaltweet
    else:
        finaltweet = dedup.finaltweet
    
    # strip html tags
    finaltweet = BeautifulSoup(finaltweet, 'html.parser').get_text()

    # truncate toot to user-defined value whatever the content is
    if len(finaltweet) > tootmaxlen:
        finaltweet = finaltweet[0:tootmaxlen-1]
        return ''.join([finaltweet[0:-3], '...'])
    else:
        return finaltweet

def send_message_dry_run(config, entrytosend, finaltweet, spoiler_text):
    '''simulate sending message using dry run mode'''
    
    # show if we are using CW
    use_cw = config.get('mastodon', 'use_cw', fallback='Y')
    
    if entrytosend:
        if use_cw == 'Y':
            logging.warning('Using CW, spoiler text: {}'.format(spoiler_text))
        else:
            finaltweet = spoiler_text + '\n' + finaltweet
        logging.warning('Would toot with visibility "{visibility}": {toot}'.format(
            toot=finaltweet,
            visibility=config.get(
                'mastodon', 'toot_visibility',
                fallback='public')))
    else:
        logging.debug('This rss entry did not meet pattern criteria. Should have not been sent')

def send_message(config, clioptions, options, entrytosend, finaltweet, spoiler_text, cache, rss):
    '''send message'''
    
    # show if we are using CW
    use_cw = config.get('mastodon', 'use_cw', fallback='Y')
    
    storeit = True
    if entrytosend and not clioptions.populate:
        if use_cw == 'Y':
            logging.debug('Using CW, spoiler text: {}'.format(spoiler_text))
        else:
            finaltweet = spoiler_text + '\n' + finaltweet
        logging.debug('Tooting with visibility "{visibility}": {toot}'.format(
            toot=finaltweet,
            visibility=config.get(
                'mastodon', 'toot_visibility',
                fallback='public')))
        twp = TootPost(config, options, finaltweet, spoiler_text)
        storeit = twp.storeit()
    else:
        logging.debug('populating RSS entry {}'.format(rss['id']))
    # in both cas we store the id of the sent tweet
    if storeit:
        cache.append(rss['id'])
