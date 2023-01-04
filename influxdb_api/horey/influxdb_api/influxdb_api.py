"""
Working with influx toolset

"""

import datetime
import os

from horey.h_logger import get_logger
from horey.common_utils.text_block import TextBlock

logger = get_logger()


class InfluxDBAPI:
    """
    InfluxDB toolset
    """
    def __init__(self):
        pass

    @staticmethod
    def parse_journalctl(file_path):
        """
        journalctl -u influxdb.service >> /tmp/journalctl.txt
        :return:
        """
        with open(file_path, encoding="utf-8") as file:
            lines = file.readlines()
        line = lines[0]
        lst_line = line.split(" ")

        # date_string = "2022-12-31_21:08:35"
        date_string = f"{lst_line[5]}_{lst_line[6]}"
        datetime_start = datetime.datetime.strptime(date_string, "%Y-%m-%d_%H:%M:%S")

        date_string = f"{lst_line[11]}_{lst_line[12]}"
        datetime_end = datetime.datetime.strptime(date_string, "%Y-%m-%d_%H:%M:%S")
        timedelta = datetime_end - datetime_start

        get, post = [], []
        for line in lines:
            if "GET " in line:
                get.append(line.strip("\n"))
            if "POST " in line:
                post.append(line.strip("\n"))

        tb_ret = TextBlock(f"Analysing requests' logs: '{os.path.basename(file_path)}'")
        post = InfluxDBAPI.parse_journalctl_post(post, timedelta.seconds)
        tb_ret.blocks.append(post)
        get = InfluxDBAPI.parse_journalctl_get(get, timedelta.seconds)
        tb_ret.blocks.append(get)
        print(tb_ret)
        return tb_ret

    @staticmethod
    def parse_journalctl_post(lines, seconds):
        """
        Parse and analise the logs.

        :param lines:
        :param seconds:
        :return:
        """

        tb_ret = TextBlock("Analysing POST requests")
        tb_ret.lines.append(f"Average requests per second: {len(lines)//seconds} rps")

        response_times = []
        response_sizes = []
        for line in lines:
            response_times.append(int(line.split(" ")[-1]))
            lst_line = line.split(" ")
            if lst_line[15] == "0":
                continue
            response_sizes.append(int(lst_line[15]))

        tb_ret.lines.append(f"Min response time: {min(response_times)} microseconds")
        tb_ret.lines.append(f"Max response time: {max(response_times)} microseconds")
        tb_ret.lines.append(f"Average response time: {sum(response_times)//len(lines)} microseconds")
        tb_ret.lines.append(f"Min sent data: {min(response_sizes)} bytes")
        tb_ret.lines.append(f"Max sent data: {max(response_sizes)} bytes")
        tb_ret.lines.append(f"Average sent data: {sum(response_sizes)//len(response_sizes)} bytes")
        return tb_ret

    @staticmethod
    def parse_journalctl_get(lines, seconds):
        """
        Parse and analise the logs.

        :param lines:
        :param seconds:
        :return:
        """

        tb_ret = TextBlock("Analysing GET requests")
        tb_ret.lines.append(f"Average requests per minute: {len(lines)*60//seconds} rpm")

        response_times = []
        response_sizes = []
        unparsable_lines = []
        for line in lines:
            if len(line) >= 49200:
                unparsable_lines.append(line)
                continue

            response_times.append(int(line.split(" ")[-1]))
            lst_line = line.split(" ")
            if lst_line[15] == "0":
                continue
            response_sizes.append(int(lst_line[15]))

        tb_ret.lines.append(f"Min response time: {min(response_times)} microseconds")
        tb_ret.lines.append(f"Max response time: {max(response_times)} microseconds")
        tb_ret.lines.append(f"Average response time: {sum(response_times)//len(lines)} microseconds")
        tb_ret.lines.append(f"Min sent data: {min(response_sizes)} bytes")
        tb_ret.lines.append(f"Max sent data: {max(response_sizes)} bytes")
        tb_ret.lines.append(f"Average sent data: {sum(response_sizes)//len(response_sizes)} bytes")
        return tb_ret
