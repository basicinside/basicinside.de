from __future__ import unicode_literals
from base64 import b64encode
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.ttypes as NoteStore
import md5
import re
import os

try:
    from config import EVERNOTE_API_TOKEN
except ImportError:
    raise ImportError("""
        Please create a config.py based on the config.py-sample
        and fill in your developer API token.
    """)


POST_DIR = os.path.normpath(
    os.path.dirname(os.path.realpath(__file__)) + "/../jekyll/_posts/")
POST_TEMPLATE = ("""---
layout: post
title:  "{title}"
date:   "{last_updated}"
categories: "{categories}"
---
{content}
""")


class NoteBook(object):
    def __init__(self, note_store):
        self.note_store = note_store

    def get_notes(self, filter="blog:"):
        notes = []
        note_filter = NoteStore.NoteFilter()
        note_filter.words = 'intitle:"blog: "'
        notes_metadata_result_spec = NoteStore.NotesMetadataResultSpec()

        notes_metadata_list = self.note_store.findNotesMetadata(
            note_filter, 0, 99, notes_metadata_result_spec)
        for note_entry in notes_metadata_list.notes:
            note_guid = note_entry.guid
            note = self.note_store.getNote(
                note_guid, True, True, False, True)
            notes.append(Note(note, self))
        return notes


class Note(object):
    def __init__(self, note, notebook):
        self.note = note
        self.notebook = notebook
        self.resources = {}
        # build a dictionary of all resources
        # media hash => base64 encoded media data
        if self.note.resources:
            for resource in self.note.resources:
                digest = md5.new(resource.data.body).hexdigest()
                self.resources[digest] = b64encode(resource.data.body)

    def updated_from_evernote(self):
        return datetime.fromtimestamp(
            self.note.updated / 1000).strftime('%Y-%m-%d %H:%M:%S')

    def created_from_evernote(self):
        return datetime.fromtimestamp(
            self.note.created / 1000).strftime('%Y-%m-%d')

    def title_from_evernote(self):
        return re.sub("blog: ", "", self.note.title)

    def content_from_evernote(self):
        def html2markdown(html):
            # replace non-letters
            html = re.sub(r'[^\x00-\x7F]+', '', html)
            # replace links
            soup = BeautifulSoup(html)
            for a in soup.findAll('a'):
                a.replaceWith("[{}]({}) ".format(a.text, a.get('href')))
            # replace evernote media tags with inline image tags
            for media in soup.findAll('en-media'):
                media.replaceWith(
                    "<img src='data:{};base64,{}' style='{}' />".format(
                        media.get('type'), self.resources[media.get('hash')],
                        media.get('style')))

            # remove tags
            markdown = re.sub(r'<.*?>', '', str(soup))
            # replace html entities
            html_replacements = [
                ('&quot;', '"'),
                ('&gt;', '>'),
                ('&lt;', '<'),
            ]
            for original, replacement in html_replacements:
                markdown = re.sub(original, replacement, markdown)
            markdown = markdown.encode('ascii', 'xmlcharrefreplace')
            return markdown
        return html2markdown(self.note.content)

    def category_from_evernote(self):
        if self.note.tagGuids:
            return self.notebook.note_store.getTag(self.note.tagGuids[0]).name
        else:
            return ""

    @property
    def filename(self):
        return "{}-{}.markdown".format(
            self.created_from_evernote(), self.note.guid)

    @property
    def content(self):
        post = {
            'title': self.title_from_evernote(),
            'last_updated': self.created_from_evernote(),
            'categories': self.category_from_evernote(),
            'content': self.content_from_evernote(),
        }
        print "Note generated: {}".format(post.get('title'))
        return POST_TEMPLATE.format(**post)


def main():
    client = EvernoteClient(token=EVERNOTE_API_TOKEN, sandbox=False)

    note_store = client.get_note_store()
    notebook = NoteBook(note_store)
    notes = notebook.get_notes()
    for note in notes:
        post_fd = open("{}/{}".format(POST_DIR, note.filename), 'w')
        post_fd.write(note.content)
        post_fd.close()


if __name__ == "__main__":
    main()
