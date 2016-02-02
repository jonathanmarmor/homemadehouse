import os

from music21.note import Note, Rest
from music21.pitch import Pitch
from music21.chord import Chord
from music21.stream import Part, Score
from music21.duration import Duration
from music21.layout import StaffGroup, ScoreLayout
from music21.instrument import fromString as get_instrument
from music21.clef import BassClef
from music21.metadata import Metadata


def write_png_with_musescore(musicxml_file_path, output_file_path, dpi=None):
    musescore_path = '/Applications/MuseScore 2.app/Contents/MacOS/mscore'

    if not output_file_path.endswith('.png'):
        output_file_path += '.png'

    command = '"{}" {} -o {} -T 0'.format(musescore_path, musicxml_file_path, output_file_path)
    if dpi:
        command += ' -r {}'.format(dpi)

    os.system(command)


def write_notation_cell(music, path, event_index):
    score = Score()

    metadata = Metadata()
    metadata.title = ''
    metadata.composer = ''
    score.insert(0, metadata)

    layout = ScoreLayout()
    layout.scalingMillimeters = 1.25
    layout.scalingTenths = 40
    score.insert(0, layout)

    for musician in music:
        instrument_name = musician['instrument']
        instrument = get_instrument(instrument_name)
        instrument.partName = instrument.instrumentName
        if instrument.instrumentName is 'Violoncello':
            instrument.partName = 'Cello'
        instrument.partAbbreviation = instrument.instrumentAbbreviation

        parts = []
        part = Part()
        parts.append(part)
        part.insert(0, instrument)

        score.insert(0, part)
        # score.insert(0, StaffGroup(parts))

        for event in musician['music']:
            pitches = event['pitches']
            dur = event['duration']
            # if not pitches or pitches == 'stop':
            #     note = Rest()
            if len(pitches) == 1:
                pitch = Pitch(pitches[0] + 60)
                note = Note(pitch)
            else:
                note = Chord(notes=[Pitch(p + 60) for p in pitches])

            duration = Duration()
            duration.fill([dur])
            note.duration = duration

            part.append(note)

    file_path = os.path.join(path, str(event_index).zfill(2))
    musicxml_file_path = file_path + '.xml'
    png_output_file_path = file_path + '.png'

    score.write('musicxml', musicxml_file_path)

    write_png_with_musescore(musicxml_file_path, png_output_file_path, dpi=600)
