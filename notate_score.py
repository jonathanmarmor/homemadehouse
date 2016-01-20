from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Part, Score
from music21.duration import Duration
from music21.layout import StaffGroup
from music21.instrument import fromString as get_instrument
# from music21.clef import BassClef


def notate_score(musician_names, instrument_names, music):
    score = Score()

    for musician_name, instrument_name in zip(musician_names, instrument_names):
        instrument = get_instrument(instrument_name)
        instrument.partName = instrument.instrumentName
        instrument.partAbbreviation = instrument.instrumentAbbreviation

        parts = []
        part = Part()
        parts.append(part)
        part.insert(0, instrument)

        score.insert(0, part)
        score.insert(0, StaffGroup(parts))

        notes = music[musician_name]

        for pitches in notes:
            if not pitches or pitches == 'stop':
                note = Rest()
            elif len(pitches) == 1:
                pitch = Pitch(pitches[0] + 60)
                note = Note(pitch)
            else:
                note = Chord(notes=[Pitch(p + 60) for p in pitches])

            duration = Duration()
            duration.fill([4.0])
            note.duration = duration

            part.append(note)

    score.show('musicxml', '/Applications/Sibelius 7.5.app')
