#!/usr/bin/env python

"""A piece of music for Sonic Liberation Players

song.title
song.composer
song.instruments
    instrument['name']
    instrument['music']
        note['duration']
        note['pitch']

"""

import random

from notate import notate

from instruments import instruments
from ensemble import Ensemble
# from graph import Graph


def make_phrase():
    phrase = []
    total_duration = 0  # in microbeats
    length = 4
    while total_duration < length:
        pitch = random.choice(['rest', 60, 61, 62, 63, 64, 65, 66, 67, 68, 62, 63, 64, 65, 66])
        duration = random.choice([.25, .5, .75, 1.0, 1.25, 1.5])
        if total_duration + duration > length:
            duration = length - total_duration

        phrase.append({
            'pitch': pitch,
            'duration': duration
        })
        total_duration += duration
    return phrase


def get_next_base_phrase(phrase1_offset, phrase1, phrase2_offset, phrase2):
    phrase1_pitch = phrase1['pitch'][0]
    phrase2_pitch = phrase2['pitch'][0]
    pitch_diff = phrase2_pitch - phrase1_pitch

    time_diff = phrase2_offset - phrase1_offset
    phrase3_offset = phrase2_offset + time_diff

    phrase3 = [{
        'pitch': n['pitch'] + pitch_diff,
        'duration': n['duration']
    } for n in phrase2]

    return phrase3_offset, phrase3


def main():
    song = Song()

    phrase1_offset = 0
    phrase1 = make_phrase()

    for n in phrase1:
        song.ensemble.oboe['music'].append({
            'pitch': n['pitch'],
            'duration': n['duration']
        })

    # TODO: Add phrase1 to an instrument

    # phrase2_offset = 2.0
    # pitch_diff = -2
    # phrase2 = [{
    #     'pitch': n['pitch'] + pitch_diff,
    #     'duration': n['duration']
    # } for n in phrase1]

    # # TODO: Add a gap of phrase2_offset and phrase2 to an instrument

    # phrase3_offset, phrase3 = get_next_base_phrase(phrase1_offset, phrase1, phrase2_offset, phrase2)

    # # TODO: figure out how to calculate phrase3's offset since the last thing this instrument played



    # length = 64
    # total_duration = 0
    # while total_duration < length:
    #     for inst in song.ensemble:
    #         gap = {
    #             'pitch': 'rest',
    #             'duration': random.choice([1.5, 1.75, 2.0, 2.25, 2.5])
    #         }
    #         inst['music'].append(gap)
    #         for n in phrase:
    #             inst['music'].append({
    #                 'pitch': n['pitch'],
    #                 'duration': n['duration']
    #             })

    #         dur = sum([n['duration'] for n in inst['music']])
    #         if dur > total_duration:
    #             total_duration = dur

    # notate(song.title, song.composer, song.ensemble._list)

    return song


class Song(object):
    title = 'Working Title'
    composer = 'Jonathan Marmor'

    def __init__(self):
        self.ensemble = Ensemble(instruments)

        # self.graph = Graph(self.ensemble)

        # self.make_music()

    # def make_music(self):
        # phrase = self.make_phrase()

        # phrase_duration = sum([n['duration'] for n in phrase])

        # # Make a list of possible gap durations
        # # the range is from a sixteenth note to 1.5 times the duration of the phrase
        # phrase_dur_times_4 = int(phrase_duration * 4)
        # gap_max = phrase_dur_times_4 + (phrase_dur_times_4 / 2)
        # gap_options = [(_ / 4.0) + .25 for _ in range(gap_max)]

        # last_instrument_name = None

        # length = 128
        # total_duration = 0
        # while total_duration < length:

        #     # pick a duration from the start of the last phrase where the next phrase will begin
        #     gap = random.choice(gap_options)

        #     # pick an instrument, that isn't the instrument that just played the phrase
        #     instrument_name = random.choice([i for i in self.ensemble.names if i not last_instrument])
        #     last_instrument_name = instrument_name

        #     # figure out the difference between the total duration already in this instrument and the starting point of the previous phrase in last instrument
        #     # then add gap to that
        #     # and append a rest of that duration to the instrument
        #     # then append the phrase
        #     # then loop

        # length = 64
        # total_duration = 0
        # while total_duration < length:
        #     for inst in self.ensemble:
        #         gap = {
        #             'pitch': 'rest',
        #             'duration': random.choice([1.5, 1.75, 2.0, 2.25, 2.5])
        #         }
        #         inst['music'].append(gap)
        #         for n in phrase:
        #             inst['music'].append({
        #                 'pitch': n['pitch'],
        #                 'duration': n['duration']
        #             })

        #         dur = sum([n['duration'] for n in inst['music']])
        #         if dur > total_duration:
        #             total_duration = dur


if __name__ == '__main__':
    main()
