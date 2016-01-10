"""This is a simplified version of notate.py that can be pasted into iPython to experiment."""

import datetime

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Part, Score
from music21.metadata import Metadata
from music21.duration import Duration
from music21.layout import StaffGroup
from music21.instrument import fromString as get_instrument
from music21.clef import BassClef


timestamp = datetime.datetime.utcnow()
metadata = Metadata()
metadata.title = 'The Title'
metadata.composer = 'Jonathan Marmor'
metadata.date = timestamp.strftime('%Y/%m/%d')

score = Score()
score.insert(0, metadata)

part = Part()
parts = [part]

oboe = get_instrument('oboe')
part.insert(0, oboe)
score.insert(0, part)
score.insert(0, StaffGroup(parts))

for dur in [[1, .5], [.25], [.25, 2]]:
    pitch = Pitch(60)
    note = Note(pitch)
    duration = Duration()
    duration.fill(dur)
    note.duration = duration

    part.append(note)

score.show('musicxml', '/Applications/Sibelius 7.5.app')
