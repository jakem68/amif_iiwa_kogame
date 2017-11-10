#!/usr/bin/env python

__author__ = 'Jan Kempeneers'

import os
import datetime

class Log(object):

    def __init__(self, logfile='c:/Users/Administrator/PycharmProjects/AMIF/log_file.txt'):
        self.log_file = logfile
        self.day_start_time = datetime.datetime.now().replace(hour=8, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        self.day_end_time = datetime.datetime.now().replace(hour=17, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
        self.day_seconds = (datetime.datetime.strptime(self.day_end_time, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(self.day_start_time, '%Y-%m-%d %H:%M:%S')).total_seconds()

    def log_entry(self, to_file):
        # log entries are formatted: 'timestamp,total/n'
        # open log file
        file_exists = os.path.isfile(to_file)
        # create timestamp
        cur_timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        if not file_exists:
            print ("log file not found, creating a new one at {}.".format(to_file))
            with open(to_file, 'w') as f:
                f.close()
        with open(to_file, 'r') as f:
            try:
                lines = f.readlines()
                # read first (oldest) entry
                firstline = lines[0]
                # read last entry
                lastline = lines[-1]
                first_entry = False
            except:
                print ('file was empty, adding the first line')
                first_entry = True
                pass
        if not first_entry:
            # read previous total from lastline
            previous_total = lastline.split(',')[1]  # previous total
            # calculate new total
            new_total = int(previous_total) + 1  # new total
        else:
            new_total = 1
        # create new entry
        new_entry = '{},{}\n'.format(cur_timestamp, new_total)
        print ("new entry is {}".format(new_entry))
        # write new entry to file
        with open(to_file, 'a') as f:
            f.write(new_entry)
        # thanks to 'with open' file closes automatically after exiting with
        pass


def main():
    l=Log()
    l.log_entry(l.log_file)

if __name__ == "__main__":
    main()
