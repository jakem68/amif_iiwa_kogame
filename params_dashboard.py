#!/usr/bin/env python

__author__ = 'Jan Kempeneers'

import datetime
import socket
import dweepy
import log
import time

# log_file = "/home/jan/temp/log_file.txt"
log_file = 'c:/Users/Administrator/PycharmProjects/AMIF/log_file.txt'
logger = log.Log(log_file)
day_start_time = datetime.datetime.strptime(logger.day_start_time, "%Y-%m-%d %H:%M:%S")
day_end_time = datetime.datetime.strptime(logger.day_end_time, "%Y-%m-%d %H:%M:%S")
production_data = {}


def read_file():
    now = datetime.datetime.now()
    str_now = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
    with open(logger.log_file, 'r') as f:
        try:
            lines = f.readlines()
        except:
            print('file not found or file empty')
            return None
    # read first (oldest) entry
    firstline = lines[0]
    # read last entry
    lastline = lines[-1]
    total_produced = int(lastline.split(',')[1])
    last_time_produced = datetime.datetime.strptime((lastline.split(',')[0]), "%Y-%m-%d %H:%M:%S")
    str_last_time_produced = datetime.datetime.strftime(last_time_produced, "%Y-%m-%d %H:%M:%S")
    first_time_produced = datetime.datetime.strptime((firstline.split(',')[0]), "%Y-%m-%d %H:%M:%S")
    str_first_time_produced = datetime.datetime.strftime(first_time_produced, "%Y-%m-%d %H:%M:%S")

    # loop through the entries to find the first value of the current day and calculate the parts produced today
    for line in lines:
        timestamp_str = line.split(',')[0]
        timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        if timestamp.date() == datetime.datetime.today().date():
            first_time_today = datetime.datetime.strptime((line.split(',')[0]), "%Y-%m-%d %H:%M:%S")
            first_total_today = int(line.split(',')[1])
            produced_today = total_produced - first_total_today + 1
            break
        else:
            produced_today = 0
            first_time_today = day_start_time
            elapsed_time_today = now - first_time_today
            elapsed_seconds_today = elapsed_time_today.total_seconds()
            time_left_today = day_end_time - now
            seconds_left_today = time_left_today.total_seconds()


    if produced_today > 1:
        elapsed_time_today = now - first_time_today
        elapsed_seconds_today = elapsed_time_today.total_seconds()
        try:
            pace_today = produced_today / elapsed_seconds_today
            time_left_today = day_end_time - now
            seconds_left_today = time_left_today.total_seconds()
            if seconds_left_today < 0:
                seconds_left_today = 0
            projected_quantity_today = produced_today + int(round(pace_today * seconds_left_today))
            production_data["projected quantity today"] = projected_quantity_today
        except:
            print("only 1 part produced so far, no forecast possible yet")
            pass
    else:
        production_data["projected quantity today"] = 0
        print ("less than two parts produced today, no forecast possible yet")

    production_data["produced today"] = produced_today
    production_data["elapsed time today"] = elapsed_seconds_today
    production_data["time left today"] = seconds_left_today
    production_data["last time produced"] = str_last_time_produced
    production_data["first time produced"] = str_first_time_produced
    production_data["total produced"] = total_produced
    production_data["time_last_message"] = str_now
    print(production_data)
    return production_data


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return (ip)


def main():
    while True:
        values = read_file()
        ip_addr = get_ip()
        values["ip address"] = ip_addr
        print (values)
        dweepy.dweet_for('kogame_iiwa', values)
        time.sleep(30)


if __name__ == "__main__":
    main()
