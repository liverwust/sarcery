import sarcery
import unittest


class TestSarParser(unittest.TestCase):
    """ During testing, rename sarcery.fact to sarcery.py """

    def test_separate_by_identifier_nominal(self):
        in_content =  {'CPU':   [ '0',  '1',  '2',  '3',  '0',  '1',  '2',  '3'],
                       '%idle': [90.1, 91.2, 93.4, 88.6, 87.1, 88.2, 89.3, 90.4],
                       '%user': [ 0.0,  1.0,  2.0,  3.0,  4.0,  5.0,  6.0, 7.9],
                       'timestamp': [1, 2, 3, 4, 5, 6, 7, 8]}
        out_content = {'0::%idle': [90.1, 87.1],
                       '1::%idle': [91.2, 88.2],
                       '2::%idle': [93.4, 89.3],
                       '3::%idle': [88.6, 90.4],
                       '0::%user': [0.0, 4.0],
                       '1::%user': [1.0, 5.0],
                       '2::%user': [2.0, 6.0],
                       '3::%user': [3.0, 7.9],
                       'timestamp': [1, 2, 3, 4, 5, 6, 7, 8]}
        self.assertDictEqual(out_content, sarcery.separate_by_identifier(in_content, 'CPU'))

    def test_parse_one_continued_section(self):
        in_file = """Linux someversion blah blah

12:00:02 AM     CPU      %usr     %nice
12:10:02 AM     all      1.47      0.00
12:10:02 AM       0      0.34      0.00
12:10:02 AM       1      0.21      0.00
12:20:01 AM     all      2.01      0.00
12:20:01 AM       0      0.43      0.00
12:20:01 AM       1      0.25      5.00
12:30:01 AM     all      1.56      0.00
12:30:01 AM       0      0.64      0.00
12:30:01 AM       1      1.62      7.00
12:40:01 AM     all      1.47      0.21
12:40:01 AM       0      2.48      0.71
12:40:01 AM       1      0.32      9.00

Average:        CPU      %usr     %nice
Average:        all      1.19      0.11
Average:          0      1.18      0.64
Average:          1      1.23      0.07

12:00:02 AM %commit  kbcommit
12:10:02 AM   11.11    111100
12:20:01 AM   11.14    111400
12:30:01 AM   17.11    171100
12:40:01 AM   33.33    333300
Average:      18.17    181725
"""
        out_structure = [{'timestamp':  ['12:10:02 AM', '12:20:01 AM', '12:30:01 AM', '12:40:01 AM', 'Average:'],
                          'all::%usr':  [         1.47,          2.01,          1.56,         1.47,        1.19],
                          '0::%usr':    [         0.34,          0.43,          0.64,         2.48,        1.18],
                          '1::%usr':    [         0.21,          0.25,          1.62,         0.32,        1.23],
                          'all::%nice': [         0.00,          0.00,          0.00,         0.21,        0.11],
                          '0::%nice':   [         0.00,          0.00,          0.00,         0.71,        0.64],
                          '1::%nice':   [         0.00,          5.00,          7.00,         9.00,        0.07]},
                         {'timestamp':  ['12:10:02 AM', '12:20:01 AM', '12:30:01 AM', '12:40:01 AM', 'Average:'],
                          '%commit':    [        11.11,         11.14,         17.11,        33.33,       18.17],
                          'kbcommit':   [       111100,        111400,        171100,       333300,      181725]}]

        self.assertDictEqual(out_structure[0], sarcery.parse_file_content(in_file.splitlines())[0])  # CPU info
        self.assertDictEqual(out_structure[1], sarcery.parse_file_content(in_file.splitlines())[1])  # memory info

    def test_analyze_sample_content(self):
        in_structure = [{'timestamp':  ['12:10:02 AM', '12:20:01 AM', '12:30:01 AM', '12:40:01 AM', 'Average:'],
                         'all::%usr':  [         1.46,          2.01,          1.56,         1.47,        1.69],
                         '0::%usr':    [         0.34,          0.43,          0.64,         2.48,        1.18],
                         '1::%usr':    [         0.21,          0.25,          1.62,         0.32,        1.23],
                         'all::%nice': [         0.00,          0.01,          0.01,         0.21,        0.11],
                         '0::%nice':   [         0.01,          0.01,          0.00,         0.71,        0.64],
                         '1::%nice':   [         0.00,          5.00,          7.00,         9.00,        0.07],
                         '%commit':    [        11.11,         11.14,         17.11,        33.33,       18.17],
                         'kbcommit':   [       111100,        111400,        171100,       333300,      181725]}]
        out_analysis = {'averages': {'all::%usr':  1.69, '0::%usr':    1.18, '1::%usr': 1.23,
                                     'all::%nice': 0.11, '0::%nice':   0.64, '1::%nice': 0.07,
                                     '%commit':   18.17, 'kbcommit': 181725},
                        'maximums': {'all::%usr':  {'measurement': 2.01,   'timestamp': '12:20:01 AM'},
                                     '0::%usr':    {'measurement': 2.48,   'timestamp': '12:40:01 AM'},
                                     '1::%usr':    {'measurement': 1.62,   'timestamp': '12:30:01 AM'},
                                     'all::%nice': {'measurement': 0.21,   'timestamp': '12:40:01 AM'},
                                     '0::%nice':   {'measurement': 0.71,   'timestamp': '12:40:01 AM'},
                                     '1::%nice':   {'measurement': 9.00,   'timestamp': '12:40:01 AM'},
                                     '%commit':    {'measurement': 33.33,  'timestamp': '12:40:01 AM'},
                                     'kbcommit':   {'measurement': 333300, 'timestamp': '12:40:01 AM'}},
                        'minimums': {'all::%usr':  {'measurement': 1.46,   'timestamp': '12:10:02 AM'},
                                     '0::%usr':    {'measurement': 0.34,   'timestamp': '12:10:02 AM'},
                                     '1::%usr':    {'measurement': 0.21,   'timestamp': '12:10:02 AM'},
                                     'all::%nice': {'measurement': 0.00,   'timestamp': '12:10:02 AM'},
                                     '0::%nice':   {'measurement': 0.00,   'timestamp': '12:30:01 AM'},
                                     '1::%nice':   {'measurement': 0.00,   'timestamp': '12:10:02 AM'},
                                     '%commit':    {'measurement': 11.11,  'timestamp': '12:10:02 AM'},
                                     'kbcommit':   {'measurement': 111100, 'timestamp': '12:10:02 AM'}}}
        self.assertDictEqual(out_analysis, sarcery.isolate_desired_fields(in_structure, ['%usr', '%nice', '%commit', 'kbcommit']))


if __name__ == '__main__':
    unittest.main()
