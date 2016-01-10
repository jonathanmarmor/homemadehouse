from collections import Counter


# class State(object):
#     def __init__(self):
#         self.events = []

#         self.harmonies = []

#     @property
#     def stats():
#         d = {}

#         return d

# def main():
#     state = State()
#     tick = 0
#     while total_duration < max_total_duration:
#         tick += 1
#         event = get_next_event(state)
#         state.events.append(event)


class Piece(object):
    def __init__(self):
        self.musicians = ['jessica', 'andrea', 'kristin', 'trevor', 'rachel']
        self.tick = 0
        self.events = []

        # `reality` Needs a better variable name
        # This contains all the things happening between events
        self.reality = []

        self.harmonies = []
        self.pitchclass_count = Counter()
        # self.pitchclass_count_no_unisons = Counter()
        # There could be 3 versions of pitch class counters:
        # 1. any event (per instrument) that has the pitchclass
        # 2. any de-duped harmony that has the pitchclass
        # 3. any de-duped harmony that has the pitchclass, but common tones
        #    between adjacent harmonies count as one occurrence

        self._event_generator = self._get_event_generator()

    def _get_event_generator(self):
        while True:
            self.tick += 1
            event = try_f(self.get_event)
            yield event

    def next(self):
        return self._event_generator.next()

    def run(self, n_events=40):
        while len(self.events) < n_events:
            event = self.next()
            if event:
                self.add_event(event)


    def _get_new_reality(self, event):
        # Make new reality: the actual music being played between events.
        new_reality = {}
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

    def add_event(self, event):
        self.events.append(event)

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

        new_pitchclasses = [p for p in harmony if p not in previous_harmony]
        # Increment pitch class counter
        for pitch in new_pitchclasses:
            self.pitchclass_count[pitch] + 1
