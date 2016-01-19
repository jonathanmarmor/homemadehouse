#!/usr/bin/env python

import random
# import datetime
# import csv
# import os
from collections import Counter, defaultdict
import argparse

import yaml

from utils import weighted_choice_lists
from harmony_utils import is_allowed, find_all_supersets


MAX_DEPTH = 100


exception_counter = Counter()


def try_f(f, args=[], kwargs={}, depth=0):
    """Dumb way to try a random process a bunch of times."""
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
PITCHCLASSES = range(12)


def spell(chord):
    # TODO detect if flats or sharps should be used
    return ' '.join([note_names[p] for p in chord])


class Piece(object):
    def __init__(self, n_events=40, config='musicians.yaml'):
        self.n_events = n_events
        self.done = False

        self.musicians = yaml.load(open(config, 'rb'))

        self.prev_state = {name: [] for name in self.musicians}
        self.prev_event = {}
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

    def _get_event_generator(self):
        while True:
            # event = self.get_event()
            event = try_f(self.get_event)
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

    def get_event(self):
        # entering, exiting, holdover_pitches = self.get_entering_exiting_and_holdover_pitches()
        entering, exiting, holdover_pitches = try_f(self.get_entering_exiting_and_holdover_pitches)

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
            raise Exception('Only harmony option is the previous harmony.')

        event = {}
        if entering:
            # event = self.pick_harmony(entering, harmony_options, holdover_pitches)
            event = try_f(self.pick_harmony, args=[entering, harmony_options, holdover_pitches])

        for name in exiting:
            event[name] = 'stop'

        return event

    def get_entering_exiting_and_holdover_pitches(self):
        changing = self.get_changing_musicians()
        entering, exiting = self.get_enterers_and_exiters(changing, self.prev_state)
        holdover_pitches = self.get_holdover_pitches(changing)

        if not entering and not is_allowed(holdover_pitches):
            raise Exception('Pitches dropped out, no new pitches are coming in, and the harmony left behind is not allowed. Try again.')

        return entering, exiting, holdover_pitches

    def pick_harmony(self, entering, harmony_options, holdover_pitches):
        pitches = {name: [] for name in entering}

        if len(harmony_options) > 1 and self.prev_harmony in harmony_options:
            harmony_options.remove(self.prev_harmony)

        # pick a harmony
        # print 'N Harmony Options:', len(harmony_options)
        harmony_options.reverse()
        harmony_weights = [int(2 ** n) for n in range(len(harmony_options))]
        new_harmony = weighted_choice_lists(harmony_options, harmony_weights)
        new_pitches = [p for p in new_harmony if p not in holdover_pitches]

        # make sure all new pitches are used
        n = 0
        while new_pitches:
            n += 1
            name = random.choice(entering)
            p = random.choice(new_pitches)
            if len(pitches[name]) < self.musicians[name]['max_notes']:
                pitches[name].append(p)
                new_pitches.remove(p)
            if n > 1000:
                raise Exception('Couldnt allocate all new pitches.')

        # make sure all musicians in entering get pitches
        n = 0
        while not all(pitches.values()):
            n += 1
            empty = [name for name in pitches if not pitches[name]]
            name = random.choice(empty)
            p = random.choice(new_harmony)
            pitches[name].append(p)
            if n > 1000:
                raise Exception('Couldnt fill all entering instruments.')

        # Add some extra notes
        if random.random() < 0.40:
            headroom = {name: self.musicians[name]['max_notes'] - len(pitches[name]) for name in entering}
            for name in headroom:
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

        for pc in PITCHCLASSES:
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
            not_eligible = [name for name in self.prev_event if self.prev_event[name] != 'stop']
            if len(not_eligible) == len(self.musicians):
                not_eligible.remove(random.choice(not_eligible))
            eligible = [name for name in self.musicians if name not in not_eligible]
            if len(eligible) == 1:
                changing = eligible[:]
            else:
                n_musicians_opts = range(1, len(eligible) + 1)
                n_musicians_weights = list(reversed([2 ** n for n in n_musicians_opts]))
                n_musicians_weights[0] = n_musicians_weights[1]
                num_changing = weighted_choice_lists(n_musicians_opts, n_musicians_weights)
                changing = random.sample(eligible, num_changing)
        return changing

    def add_event(self, event):

        self.score.append(event)

        self.prev_event = event

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
        print 'new_pitchclasses', new_pitchclasses
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

    # Reporting, displaying

    def report_score(self):
        for i, event in enumerate(self.score):
            print i + 1
            for name in sorted(event.keys()):
                action = event[name]
                if action != 'stop':
                    action = spell(event[name])
                print '  {:>10} {}'.format(name, action)
            print

    def report_rhythm(self):
        for name in self.grid:
            line = []
            for event in self.grid[name]:
                if event == [] or event == 'stop':
                    line.append(' ')
                else:
                    line.append('-')
            print '{:<15}  {}'.format(name, ''.join(line))

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

        from harmony_utils import get_all_transpositions, allowed_chord_types
        # Count Chord Types
        chord_type_counter = Counter()
        chords = c.keys()

        for chord in chords:
            transpositions = get_all_transpositions(chord)
            for t in transpositions:
                if t in allowed_chord_types:
                    chord_type_counter[t] += 1
                    continue
        print
        print 'Number of different chord types: ', len(chord_type_counter)
        for k, n in chord_type_counter.most_common():
            print n, k

        return lines

    # def to_csv(self):
    #     now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    #     if not os.path.isdir('exports'):
    #         os.mkdir('exports')
    #     with open('exports/two_three_four_{}.csv'.format(now), 'wb') as f:
    #         writer = csv.writer(f)
    #         for i, event in enumerate(self.score):
    #             line_number = i + 1
    #             if len(event) > 1:
    #                 writer.writerow([line_number, None, None])
    #                 line_number = None
    #             for name in event:
    #                 action = event[name]
    #                 if action == 'stop':
    #                     action = None
    #                 else:
    #                     action = spell(event[name])
    #                 writer.writerow([line_number, name, action])

    def reports(self):
        print
        self.report_score()
        print
        self.report_rhythm()
        print
        self.report_harmonies()
        print
        print exception_counter.most_common()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', default='musicians.yaml', help='Config file defining the musicians.')
    parser.add_argument('--events', '-e', default=40, help='The number of events to make.', type=int)
    args = parser.parse_args()

    p = Piece(n_events=args.events, config=args.config)
    # p.test()
    p.run()
    p.reports()
