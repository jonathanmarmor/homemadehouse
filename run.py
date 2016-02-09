#!/usr/bin/env python

from argparse import ArgumentParser
from collections import Counter

from feb3 import Piece


class Runner(object):
    def __init__(self, test=False, max_depth=500):
        self.test = test
        self.max_depth = max_depth

    def get_piece(self, n_events=40, quentin=False):
        while True:
            self.exception_counter = Counter()
            p = Piece(self, n_events=n_events, quentin=quentin)
            p.run()
            if p.gaps:
                return p

    def try_f(self, f, args=[], kwargs={}, depth=0):
        """Dumb way to try a random process a bunch of times."""
        if self.test:
            return f(*args, **kwargs)
        depth += 1
        try:
            return f(*args, **kwargs)
        except Exception as e:
            self.exception_counter['{}: {}'.format(f.__name__, e.message)] += 1
            if depth == self.max_depth:
                msg = "C'mon, you tried {} {} times. Fix the code already. Exception: {}"
                msg = msg.format(f.__name__, self.max_depth, e)
                print msg
                raise e
            return self.try_f(f, args=args, kwargs=kwargs, depth=depth)

    def report_exceptions(self):
        report = ['Exceptions Report']
        for exception, count in self.exception_counter.most_common():
            line = '{:<6}{}'.format(count, exception)
            report.append(line)

        return '\n'.join(report)


def cli():
    parser = ArgumentParser()

    # Options for testing
    parser.add_argument('--test', '-t', action='store_true')
    parser.add_argument('--max-depth', '-m', default=500,
        help='The maximum number of exceptions before quitting retries.',
        type=int)

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

    runner = Runner(test=args.test, max_depth=args.max_depth)

    p = runner.get_piece(n_events=args.events, quentin=args.quentin)

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
        print runner.report_exceptions()
        print

    if args.reality:
        p.report_reality()
        print

    if args.all_reports:
        p.reports()
        print
        print runner.report_exceptions()
        print


if __name__ == '__main__':
    cli()
