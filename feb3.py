#!/usr/bin/env python

import os
import datetime
import random
from collections import Counter, defaultdict
import argparse
import json

from utils import weighted_choice_lists, weighted_choice_dict
from harmony_utils import (is_allowed, find_all_supersets,
    get_all_transpositions, allowed_chord_types)
from notate_score import notate_score
from write_notation_cell import write_notation_cell


TEST = False
MAX_DEPTH = 500


exception_counter = Counter()


def try_f(f, args=[], kwargs={}, depth=0):
    """Dumb way to try a random process a bunch of times."""
    if TEST:
        return f(*args, **kwargs)
    depth += 1
    try:
        return f(*args, **kwargs)
    except Exception as e:
        exception_counter['{}: {}'.format(f.__name__, e.message)] += 1
        if depth == MAX_DEPTH:
            print "C'mon, you tried {} {} times. Fix the code already. Exception: {}".format(f.__name__, MAX_DEPTH, e)
            raise e
        return try_f(f, args=args, kwargs=kwargs, depth=depth)


note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def spell(chord):
    return ' '.join([note_names[p] for p in chord])


def funny_range(steps, top, bottom):
    """get `steps` numbers equally distributed between `top` and `bottom`"""
    if steps == 0:
        return []
    if steps == 1:
        return [top]
    interval = (top - bottom) / (steps - 1)
    return [top - (interval * step) for step in range(steps)]


class Piece(object):
    def __init__(self, n_events=40, quentin=False):
        self.n_events = n_events
        self.done = False
        self.n = 0
        self.exception_counter = exception_counter

        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        self.path = 'output/house_{}'.format(self.timestamp)
        os.mkdir(self.path)
        self.backup_path = os.path.join(self.path, 'backup.json')
        self.dont_save = ['_event_generator', 'n', 'prev_harmony', 'prev_state', ]
        self.counters = ['pc_counter', 'pitchclass_count', 'exception_counter']

        self.musicians = {
            'Andrea': {
                'instrument': 'Flute',
                'max_notes': 1
            },
            'Jessica': {
                'instrument': 'Voice',
                'max_notes': 1
            },
            'Kristin': {
                'instrument': 'Oboe',
                'max_notes': 1
            },
            'Rachel': {
                'instrument': 'Cello',
                'max_notes': 2
            },
            'Trevor': {
                'instrument': 'Piano',
                'max_notes': 10
            }
        }
        self.musicians_score_order = [
            'Jessica',
            'Andrea',
            'Kristin',
            'Trevor',
            'Rachel'
        ]
        self.soloist = 'Jessica'
        self.non_soloist_starters = [
            'Andrea',
            'Kristin',
            'Rachel'
        ]

        if quentin:
            self.musicians = {
                'Quentin': {
                    'instrument': 'Organ',
                    'max_notes': 10
                },
                'Nicola': {
                    'instrument': 'Piano',
                    'max_notes': 10
                },
                'Kristin': {
                    'instrument': 'Oboe',
                    'max_notes': 1
                },
                'Singer': {
                    'instrument': 'Percussion',
                    'max_notes': 1
                },
                'Marmor': {
                    'instrument': 'Percussion',
                    'max_notes': 1
                },
                'Andreas': {
                    'instrument': 'Guitar',
                    'max_notes': 3
                }
            }
            self.musicians_score_order = [
                'Kristin',
                'Andreas',
                'Quentin',
                'Nicola',
                'Singer',
                'Marmor'
            ]
            self.soloist = 'Kristin'
            self.non_soloist_starters = [
                'Andreas',
                'Quentin',
                'Nicola',
                'Singer',
                'Marmor'
            ]

        self.instrument_names = [self.musicians[name]['instrument'] for name in self.musicians_score_order]

        self.prev_state = {name: [] for name in self.musicians}
        self.prev_harmony = ()

        self.score = []
        self.grid = {name: [] for name in self.musicians}

        # `reality` Needs a better variable name
        # This contains all the things happening between events
        self.reality = []
        self.harmonies = []

        # Keep one or the other of these counters. pitchclass_count is a newer implementation and probably more correct.
        self.pitchclass_count = Counter()  #
        self.pc_counter = Counter()

        self._event_generator = self._get_event_generator()

    def __repr__(self):
        return self.reports()

    def _get_event_generator(self):
        while True:
            event = try_f(self.make_event)
            if event:
                self.add_event(event)
            yield event

    def next(self):
        return self._event_generator.next()

    def run(self, n_events=None):
        if not n_events:
            n_events = self.n_events
        while not self.done:
            self.next()

        self.count_gaps()

        print 'SAVING TO {}'.format(self.backup_path)
        self.save()

    def make_event(self):
        # Choose which musicians will start and stop playing. Get the set of
        # pitches that will sustain from the previous state.
        entering, exiting, holdover_pitches = try_f(self.get_entering_exiting_and_holdover_pitches)

        # Get harmony options
        harmony_options = self.get_harmony_options(holdover_pitches)

        event = {}
        if entering:
            # Pick a harmony and which instruments will play any new pitches
            # event = self.pick_harmony(entering, harmony_options, holdover_pitches)
            event = try_f(self.pick_harmony, args=[entering, harmony_options, holdover_pitches])

        # If an instrument is stopping, add stop to the event
        for name in exiting:
            event[name] = 'stop'

        return event

    def get_entering_exiting_and_holdover_pitches(self):
        changing = self.get_changing_musicians()
        entering, exiting = self.get_enterers_and_exiters(changing, self.prev_state)
        holdover_pitches = self.get_holdover_pitches(changing)

        if not entering and not is_allowed(holdover_pitches):
            raise Exception('Pitches dropped out, no new pitches are coming in, and the harmony left behind is not allowed')

        return entering, exiting, holdover_pitches

    def get_harmony_options(self, holdover_pitches):
        if holdover_pitches:
            harmony_options = find_all_supersets(holdover_pitches)
        else:
            # Choose a new pitch
            # print
            # print 'no holdovers. pc_counter:', self.pc_counter
            new_seed = self.get_new_seed()
            # print 'new seed', new_seed
            harmony_options = find_all_supersets([new_seed])

        if self.prev_harmony in harmony_options:
            harmony_options.remove(self.prev_harmony)

        if not harmony_options:
            raise Exception('Only harmony option is the previous harmony')

        # Make weights
        harmony_options.reverse()
        harmony_weights = [int(1.9 ** n) for n in range(len(harmony_options))]

        # Put options and weights into a dictionary
        harmony_options = {opt: weight for opt, weight in zip(harmony_options, harmony_weights)}

        # Reduce repetitions of harmonies
        for h in self.harmonies:
            h = tuple(h)
            if h in harmony_options:
                harmony_options[h] = harmony_options[h] / 2.0

        # Reduce repetitions of pitch classes
        count_of_pitchclasses_used = len(self.pitchclass_count)
        weights_to_reduce = funny_range(count_of_pitchclasses_used, 12.0, 4.0)
        for pc_and_count, weight in zip(self.pitchclass_count.most_common(), weights_to_reduce):
            pc, count = pc_and_count
            for h in harmony_options:
                if pc in h:
                    h = tuple(h)
                    harmony_options[h] = harmony_options[h] / float(weight)

        return harmony_options

    def pick_harmony(self, entering, harmony_options, holdover_pitches):
        # The total number of pitches the ensemble of entering musicians can play
        total_max_notes = sum([self.musicians[name]['max_notes'] for name in entering])

        # Choose a new harmony
        new_harmony = weighted_choice_dict(harmony_options)
        new_pitches = [p for p in new_harmony if p not in holdover_pitches]

        # If there are more new pitches than the ensemble of musicians can play
        # then refine the available options and weights and choose another harmony
        while len(new_pitches) > total_max_notes:

            # So don't allow this harmony to be chosen again
            if new_harmony in harmony_options:
                del harmony_options[new_harmony]

            # If all the harmonies have been tried and they all have more new
            # pitches than the ensemble can play, then raise an exception
            # and try with a new set of harmony options
            if not harmony_options:
                raise Exception('All harmony options had more new pitches than instruments could play')

            # Choose a new harmony from the options
            new_harmony = weighted_choice_dict(harmony_options)
            new_pitches = [p for p in new_harmony if p not in holdover_pitches]

        # Assign the new pitches to instruments
        pitches = {name: [] for name in entering}
        while new_pitches:
            name = random.choice(entering)

            # When cello plays two notes, it should be a fifth
            # TODO: Make work when Rachel isn't playing :)
            if name is 'Rachel' and len(pitches[name]) == 1:
                existing_pitch = pitches[name][0]
                # Fifths
                target_pitches = [(existing_pitch + 7) % 12, (existing_pitch + 5) % 12]
                target_pitches = [t for t in target_pitches if t in new_pitches]
                if target_pitches:
                    p = random.choice(target_pitches)
                    pitches[name].append(p)
                    new_pitches.remove(p)
                    continue
                else:
                    if len(entering) == 1:
                        p = random.choice(new_pitches)
                        if len(pitches[name]) < self.musicians[name]['max_notes']:
                            pitches[name].append(p)
                            new_pitches.remove(p)
            else:
                p = random.choice(new_pitches)
                if len(pitches[name]) < self.musicians[name]['max_notes']:
                    pitches[name].append(p)
                    new_pitches.remove(p)

        # Make sure all musicians entering get pitches
        n = 0
        while not all(pitches.values()):
            n += 1
            empty = [name for name in pitches if not pitches[name]]
            name = random.choice(empty)
            p = random.choice(new_harmony)
            pitches[name].append(p)
            if n > 1000:
                raise Exception('Couldnt fill all entering instruments')

        # Add some extra notes
        if random.random() < 0.7:
            headroom = {name: self.musicians[name]['max_notes'] - len(pitches[name]) for name in entering}
            for name in headroom:

                # When cello plays two notes, it should be a fifth
                # TODO: Make work when Rachel isn't playing :)
                if name is 'Rachel' and len(pitches[name]) == 1:
                    existing_pitch = pitches[name][0]
                    # Fifths
                    target_pitches = [(existing_pitch + 7) % 12, (existing_pitch + 5) % 12]
                    target_pitches = [t for t in target_pitches if t in new_harmony]
                    if target_pitches:
                        p = random.choice(target_pitches)
                        pitches[name].append(p)
                else:
                    pitch_options = [p for p in new_harmony if p not in pitches[name]]
                    upper = min([len(pitch_options), headroom[name]])
                    if upper:
                        n_pitches = 1
                        if upper > 1:
                            n_pitches = random.randint(1, upper)
                        ps = random.sample(pitch_options, n_pitches)
                        pitches[name].extend(ps)

        for name in pitches:
            pitches[name].sort()

        return pitches

    def get_new_seed(self):
        # Randomly choose from the pitchclasses that have occurred the least
        pcs_by_count = defaultdict(list)

        for pc in range(12):
            count = self.pc_counter[pc]
            pcs_by_count[count].append(pc)

        lowest_count = min(pcs_by_count.keys())
        return random.choice(pcs_by_count[lowest_count])

    def get_holdover_pitches(self, changing):
        # Get pitches that are sustaining from previous
        holdover_pitches = []
        not_changing = [name for name in self.musicians if name not in changing]
        holdovers = [name for name in not_changing if self.prev_state[name]]
        for name in holdovers:
            for p in self.prev_state[name]:
                if p not in holdover_pitches:
                    holdover_pitches.append(p)
        holdover_pitches.sort()
        return holdover_pitches

    def get_enterers_and_exiters(self, changing, previous_state):
        # if already playing, stop
        entering = []
        exiting = []
        for name in changing:
            if not previous_state.get(name):
                entering.append(name)
            else:
                exiting.append(name)
        return entering, exiting

    def get_changing_musicians(self):
        if self.n == 0:
            return self.non_soloist_starters + [self.soloist]

        if self.n == 1:
            return self.non_soloist_starters

        n_events_remaining = self.n_events - len(self.score)
        if n_events_remaining <= len(self.musicians):
            # End game, everyone needs to stop
            playing = [name for name in self.prev_state if self.prev_state[name]]
            if not playing:
                # We're done.
                self.done = True
                return []
            if len(playing) == 1:
                changing = playing[:]
            else:
                n_musicians_opts = range(1, len(playing) + 1)
                n_musicians_weights = list(reversed([2 ** n for n in n_musicians_opts]))
                n_musicians_weights[0] = n_musicians_weights[1]
                num_changing = weighted_choice_lists(n_musicians_opts, n_musicians_weights)
                changing = random.sample(playing, num_changing)
        else:

            eligible = self.get_eligible_to_change()

            if len(eligible) == 0:
                raise Exception('No one is eligible to change.')

            if len(eligible) == 1:
                changing = eligible
            else:
                num_changing = self.choose_number_changing(eligible)
                changing = random.sample(eligible, num_changing)

        return changing

    def get_eligible_to_change(self, depth=10):
        # If an instrument started in the last event then it can only rarely
        # change in this event
        prev_event = {}
        if self.score:
            prev_event = self.score[-1]
        not_eligible = [name for name in prev_event if prev_event[name] != 'stop' and random.random() < .85]

        # The soloist should play through the first three events
        if 1 < self.n < 4:
            not_eligible.append(self.soloist)

        if self.n > 3:
            for name in self.musicians_score_order:

                # If the instrument just stopped, make it less likely to
                # start now
                if self.score[-1].get(name) is 'stop' and \
                        name not in not_eligible and \
                        random.random() < .75:
                    not_eligible.append(name)

                # If the instrument started then continued, make it less
                # likely to start now.
                if name not in self.score[-1] and \
                        self.score[-2].get(name) is not None and \
                        self.score[-2].get(name) is not 'stop' and \
                        name not in not_eligible and \
                        random.random() < .5:
                    not_eligible.append(name)

                # If the instrument didn't change (was resting or playing)
                # in the last event, half the time they are inelligible
                if name not in self.score[-1] and \
                        name not in not_eligible and \
                        random.random() < .5:
                    not_eligible.append(name)

        eligible = [name for name in self.musicians_score_order if name not in not_eligible]
        return eligible

    def choose_number_changing(self, eligible):
        if self.n == 2:
            return random.choice([1, 2])

        max_n_musicians = len(eligible) + 1
        n_musicians_opts = range(1, max_n_musicians)
        n_musicians_weights = list(reversed([2 ** n for n in n_musicians_opts]))
        n_musicians_weights[0] = n_musicians_weights[1]
        return weighted_choice_lists(n_musicians_opts, n_musicians_weights)

    def add_event(self, event):
        self.score.append(event)
        self.n += 1

        self.prev_state = {}
        for name in event:
            self.prev_state[name] = event[name]
            if event[name] == 'stop':
                self.prev_state[name] = []

        for name in event:
            self.grid[name].append(event[name])

        not_changing = [name for name in self.musicians if name not in event]
        for name in not_changing:
            prev = []
            if self.grid[name]:
                prev = self.grid[name][-1]
            if prev == 'stop':
                prev = []
            self.grid[name].append(prev)
            self.prev_state[name] = prev

        self.prev_harmony = self.get_harmony()
        for p in self.prev_harmony:
            self.pc_counter[p] += 1

        # Extend reality :)
        new_reality = self._get_new_reality(event)
        self.reality.append(new_reality)

        # Calculate new harmony and append to list of harmonies
        previous_harmony = []
        if len(self.harmonies):
            previous_harmony = self.harmonies[-1]

        harmony = []
        for musician in new_reality:
            pitches = new_reality[musician]
            harmony.extend(pitches)
        harmony = list(set(harmony))
        harmony.sort()
        self.harmonies.append(harmony)

        # Count pitchclasses
        new_pitchclasses = [p for p in harmony if p not in previous_harmony]
        # print 'new_pitchclasses', new_pitchclasses
        # Increment pitch class counter
        for pitch in new_pitchclasses:
            self.pitchclass_count[pitch] += 1

    def _get_new_reality(self, event):
        # Make new reality: the actual music being played between events.
        new_reality = {}

        previous_reality = {}
        if len(self.reality):
            previous_reality = self.reality[-1]

        for musician in self.musicians:
            previous = previous_reality.get(musician)
            action = event.get(musician)

            if action and action is not 'stop':
                # Was playing ==> New content ==> Add from event
                # Wasn't playing ==> New content ==> Add from event
                new_reality[musician] = action

            if previous and not action:
                # Was playing ==> Not in event ==> Add from previous reality
                new_reality[musician] = previous

            # Was playing ==> Stop ==> Do nothing
            # Wasn't playing ==> Not in event ==> Do nothing
            # Wasn't playing ==> Stop ==> Do nothing (not possible)

        return new_reality

    def get_harmony(self):
        pitches = []
        for name in self.grid:
            if self.grid[name][-1] and self.grid[name][-1] is not 'stop':
                for p in self.grid[name][-1]:
                    if p not in pitches:
                        pitches.append(p)
        pitches.sort()
        return tuple(pitches)

    def count_gaps(self):
        self.gaps = 0
        for h in self.harmonies[:-1]:
            if not h:
                self.gaps += 1

    # Reporting, displaying

    def notate_harmonies(self):
        notate_score(
            self.musicians_score_order,
            self.instrument_names,
            self.grid
        )

    def report_score(self):
        for index, event in enumerate(self.score):
            print index + 1
            for name in [n for n in self.musicians_score_order if n in event]:
                action = event[name]
                if action != 'stop':
                    action = spell(event[name])
                # instrument = self.musicians[name]['instrument']
                print '  {:>12} {}'.format(name, action)
            print

    def report_rhythm(self):
        max_name_length = max([len(n) for n in self.musicians_score_order])
        label_template = '{{:<{}}}  '.format(max_name_length)
        lines = []
        for name in self.musicians_score_order:
            line = []
            for event in self.grid[name]:
                if event == [] or event == 'stop':
                    line.append(' ')
                else:
                    line.append('-')

            line = label_template.format(name) + ''.join(line)
            lines.append(line)
        return '\n'.join(lines)

    def report_harmonies(self):
        c = Counter()
        lines = []
        actual_length = len(self.grid[self.grid.keys()[0]])
        for e in range(actual_length):
            pitches = []
            for name in self.musicians:
                if self.grid[name][e] != 'stop':
                    for p in self.grid[name][e]:
                        if p not in pitches:
                            pitches.append(p)
            harmony = tuple(sorted(pitches))
            c[harmony] += 1
            line = []
            for pc in range(12):
                if pc in pitches:
                    line.append('{:<3}'.format(pc))
                else:
                    line.append('   ')
            lines.append(''.join(line))
        for line in lines:
            print line
        print
        print 'Number of different chords: ', len(c)
        for k, n in c.most_common():
            print n, k

        print
        chord_types_counter = self.count_chord_types(self.harmonies)
        print 'Number of different chord types: ', len(chord_types_counter)
        for chord_type, count in chord_types_counter.most_common():
            print '{:<5} {}'.format(str(count), str(chord_type))

        return lines

    def count_chord_types(self, chords):
        [c.sort() for c in chords]
        chords = [tuple(c) for c in chords]

        chord_type_counter = Counter()

        for chord in chords:
            transpositions = get_all_transpositions(chord)
            for t in transpositions:
                if t in allowed_chord_types:
                    chord_type_counter[t] += 1
                    continue

        return chord_type_counter

    def report_reality(self):
        print ''.join(['{:<12}'.format(name) for name in self.musicians_score_order])
        for item in self.reality:
            print ''.join(['{:<12}'.format(' '.join([str(pc) for pc in item.get(name, [])])) for name in self.musicians_score_order])

    def pngs(self):
        for event_index, event in enumerate(self.score):
            if not any([True for n in event if event[n] != 'stop']):
                continue

            event_index += 1
            music = []

            for name in [n for n in self.musicians_score_order if n in event]:
                action = event[name]
                if action != 'stop':
                    musician = {
                        'instrument': self.musicians[name]['instrument'],
                        'music': [
                            {
                                'pitches': action,
                                'duration': 4.0
                            }
                        ],
                    }
                    music.append(musician)

            write_notation_cell(music, self.path, event_index)

    def reports(self):
        print
        self.report_score()
        print
        print self.report_rhythm()
        print
        self.report_harmonies()
        print
        print 'Exceptions Report'
        for exception, count in exception_counter.most_common():
            print count, exception
        print

        self.report_reality()
        return ''

    def save(self):
        d = {key: self.__dict__[key] for key in self.__dict__ if key not in self.dont_save}
        for key in self.counters:
            d[key] = list(d[key].elements())
        json_string = json.dumps(d)

        with open(self.backup_path, 'w') as f:
            f.write(json_string)

    def load(self, path):
        backup_path = os.path.join(path, 'backup.json')
        with open(backup_path, 'r') as f:
            json_string = f.read()
        d = json.loads(json_string)

        for key in d:
            if key in self.counters:
                self.__dict__[key] = Counter(d[key])
            else:
                self.__dict__[key] = d[key]


def get_piece(n_events=40, quentin=False):
    while True:
        p = Piece(n_events=n_events, quentin=quentin)
        p.run()
        if p.gaps:
            break
    return p


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', '-t', action='store_true')

    # Options for what the music will be like
    parser.add_argument('--events', '-e', default=40,
        help='The number of events to make.', type=int)

    parser.add_argument('--quentin', '-q', action='store_true',
        help='Use Quentin band instrumentation rather than the default Sonic Lib ensemble')

    # Output options
    parser.add_argument('--notate_harmonies', '-n', action='store_true',
        help='Open harmonies in Sibelius')

    parser.add_argument('--pngs', '-p', action='store_true',
        help='Make PNG images of notation of each cell')

    parser.add_argument('--score', '-s', action='store_true',
        help='Print the score to the screen')

    parser.add_argument('--rhythm', '-r', action='store_true',
        help='Print rhythm report to the screen')

    parser.add_argument('--harmonies', '-H', action='store_true',
        help='Make PNG images of notation of each cell')

    parser.add_argument('--exceptions', '-x', action='store_true',
        help='Print exceptions report to the screen')

    parser.add_argument('--reality', '-l', action='store_true',
        help='Print "reality" report to the screen')

    parser.add_argument('--all-reports', '-a', action='store_true',
        help='Print all reports to the screen')

    args = parser.parse_args()

    if args.test:
        TEST = True

    p = get_piece(n_events=args.events, quentin=args.quentin)

    if args.pngs:
        p.pngs()

    if args.notate_harmonies:
        p.notate_harmonies()

    if args.score:
        p.report_score()
        print

    if args.rhythm:
        print p.report_rhythm()
        print

    if args.harmonies:
        p.report_harmonies()
        print

    if args.exceptions:
        print
        print 'Exceptions Report'
        for exception, count in exception_counter.most_common():
            print count, exception
        print

    if args.reality:
        p.report_reality()
        print

    if args.all_reports:
        p.reports()
        print
