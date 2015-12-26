import evernote.edam.type.ttypes as Types
import evernote.edam.notestore.ttypes as NoteStore
import os
import re

from datetime import datetime
from evernote.api.client import EvernoteClient
try:
    from config import EVERNOTE_API_TOKEN
except ImportError:
    raise ImportError("""
        Please create a config.py based on the config.py-sample
        and fill in your developer API token.
    """)


POST_DIR= os.path.normpath(
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

    def get_notes(self, filter="blog: "):
        notes = []
        note_filter = NoteStore.NoteFilter()
        note_filter.words = 'intitle:"{}"'.format(filter)
        notes_metadata_result_spec = NoteStore.NotesMetadataResultSpec()

        notes_metadata_list = self.note_store.findNotesMetadata(
            note_filter, 0, 1, notes_metadata_result_spec)
        for note_entry in notes_metadata_list.notes:
            note_guid = note_entry.guid
            note = self.note_store.getNote(
                note_guid, True, False, False, False)
            notes.append(Note(note, self))
        return notes


class Note(object):
    def __init__(self, note, notebook):
        self.note = note
        self.notebook = notebook

    def updated_from_evernote(self):
        return datetime.fromtimestamp(
            self.note.updated / 1000).strftime('%Y-%m-%d %H:%M:%S')

    def created_from_evernote(self):
        return datetime.fromtimestamp(
            self.note.created / 1000).strftime('%Y-%m-%d')

    def title_from_evernote(self):
        return re.sub("blog: ", "", self.note.title)

    def content_from_evernote(self):
        content_without_html = re.sub("<.*?>", "", self.note.content)
        content_proper_quotes = re.sub("&quot;", '"', content_without_html)
        content_proper_gt = re.sub("&gt;", '>', content_proper_quotes)
        content_proper_lt = re.sub("&lt;", '<', content_proper_gt)

        return content_proper_lt

    def category_from_evernote(self):
        categories = []
        for tagguid in self.note.tagGuids:
            tagobj = self.notebook.note_store.getTag(tagguid)
            categories.append(tagobj.name)
        return " ".join(categories)

    @property
    def filename(self):
        return "{}-{}.markdown".format(
            self.created_from_evernote(), self.note.guid)

    @property
    def content(self):
        post = {
            'title': self.title_from_evernote(),
            'last_updated': self.updated_from_evernote(),
            'categories': self.category_from_evernote(),
            'content': self.content_from_evernote(),
        }
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


main()
