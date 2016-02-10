import os
import json
import datetime
from collections import Counter

from harmony_utils import get_all_transpositions, allowed_chord_types
from notate_score import notate_score
from write_notation_cell import write_notation_cell


note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def spell(chord):
    return ' '.join([note_names[p] for p in chord])


class Grid(object):
    dont_save = ['_event_generator', 'n', 'try_f']
    counters = ['pc_counter', 'pitchclass_count']

    def __repr__(self):
        return self.reports()

    @property
    def previous_state(self):
        if self.reality:
            return self.reality[-1]
        else:
            return {name: [] for name in self.musicians_score_order}

    def add_event(self, event):
        self.score.append(event)
        self.n += 1

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

        # Extend reality :)
        new_reality = self._get_new_reality(event)
        self.reality.append(new_reality)

        # Calculate new harmony and append to list of harmonies
        previous_harmony = []
        if self.harmonies:
            previous_harmony = self.harmonies[-1]

        harmony = []
        for musician in new_reality:
            pitches = new_reality[musician]
            harmony.extend(pitches)
        harmony = list(set(harmony))
        harmony.sort()
        harmony = tuple(harmony)
        self.harmonies.append(harmony)

        for p in harmony:
            self.pc_counter[p] += 1

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
        self.report_reality()
        return ''

    def save(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        path = 'output/house_{}'.format(timestamp)
        os.mkdir(path)
        self.backup_path = os.path.join(path, 'backup.json')

        print 'SAVING TO {}'.format(self.backup_path)

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
