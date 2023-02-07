"""
Working with influx toolset

"""

import datetime
import os
import json
import urllib.parse
import requests
from horey.h_logger import get_logger
from horey.common_utils.text_block import TextBlock

logger = get_logger()


class InfluxDBAPI:
    """
    InfluxDB toolset
    """
    def __init__(self, configuration):
        self.configuration = configuration
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "text/plain",
                "User-Agent": "python/pyzabbix",
                "Cache-Control": "no-cache",
            }
        )

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

    def get(self, request_params):
        """
        GET request.

        :param request_params:
        :return:
        """
        response = self.session.get(self.generate_request(request_params), timeout=60)

        try:
            return response.json()
        except Exception as inst:
            logger.error(repr(inst))
            logger.error(response.text)
            raise

    def post(self, request_params, data):
        """
        POST request.

        :param request_params:
        :param data:
        :return:
        """

        response = self.session.post(self.generate_request(request_params), data=data.encode("utf-8"), timeout=60)

        if response.status_code not in [200, 204]:
            raise RuntimeError(response.text)

        return response

    def generate_request(self, request_params):
        """
        Generate request from address, API url and request params.

        :param request_params:
        :return:
        """
        return self.configuration.server_address + "/" + request_params.strip("/")

    def init_measurements(self, db_name):
        """
        Init measurements.

        :param db_name:
        :return:
        """
        ret = self.get(f"query?db={db_name}&q=" + urllib.parse.quote_plus('SHOW MEASUREMENTS'))
        return ret

    def yield_series(self, db_name, measurement):
        """
        Init measurements.

        :param db_name:
        :return:
        """

        offset = 0
        limit = 100000
        limit = 10000
        while True:
            response = self.get(f"query?db={db_name}&q=" + urllib.parse.quote_plus(f'SELECT * FROM "{measurement}" LIMIT {limit} OFFSET {offset}'))

            measurement_series = self.extract_values_from_response(response)
            if measurement_series is None:
                break
            offset += len(measurement_series["values"])
            logger.info(f"Total fetched count: {offset}")
            yield measurement_series

    @staticmethod
    def extract_values_from_response(response):
        """
        Extract series' values from server response.

        :param response:
        :return:
        """

        if list(response.keys()) != ["results"]:
            raise RuntimeError(response.keys())

        if len(response["results"]) != 1:
            raise RuntimeError(len(response["results"]))
        results = response["results"][0]
        if list(results.keys()) != ["statement_id", "series"]:
            if "series" not in results:
                return None
            raise RuntimeError('list(results.keys()) != ["statement_id", "series"]')
        measurements_series = results["series"]
        if len(measurements_series) != 1:
            raise RuntimeError(len(measurements_series))
        return measurements_series[0]

    def get_measurement_tag_keys(self, db_name, measurement):
        """
        Get tag names.

        :param db_name:
        :param measurement:
        :return:
        """

        ret = self.get(f"query?db={db_name}&q=" + urllib.parse.quote_plus(f"show tag keys from {measurement}"))
        return [value[0] for value in ret["results"][0]["series"][0]["values"]]

    def get_measurement_fields_types(self, db_name, measurement):
        """
        Get fields to types mapping.

        :param db_name:
        :param measurement:
        :return:
        """

        ret = self.get(f"query?db={db_name}&q=" + urllib.parse.quote_plus(f"show field keys from {measurement}"))
        mapping = {"float": float, "integer": int, "string": str, "boolean": bool}
        return {value[0]: mapping[value[1]] for value in ret["results"][0]["series"][0]["values"]}

    @staticmethod
    def field_value_to_str(field_name, value, fields_types=None):
        """
        Format 'key=value' based on type.

        :param fields_types:
        :param field_name:
        :param value:
        :return:
        """
        if isinstance(value, float):
            if fields_types is not None and fields_types[field_name] != float:
                raise ValueError("Cast error")

            value = str(value)
            if value.endswith(".0"):
                value = value[:-2]
            return f"{field_name}={value}"

        if isinstance(value, bool):
            if fields_types is not None and fields_types[field_name] != bool:
                raise ValueError("Cast error")
            return f"{field_name}={str(value).lower()}"

        if isinstance(value, int):
            if fields_types is not None and fields_types[field_name] != int:
                raise ValueError(f"Cast error while inserting field '{field_name}' value '{value}' of type '{type(value)}'."
                                 f" InfluxDB expects type '{fields_types[field_name]}'")
            return f"{field_name}={str(value)}i"

        if isinstance(value, str):
            if fields_types is not None and fields_types[field_name] != str:
                raise ValueError("Cast error")
            new_value = value.translate(str.maketrans({'"': r"\"", "\\": r"\\"}))
            return f'{field_name}="{new_value}"'

        raise ValueError(f"{field_name}: {value}")

    # pylint: disable= too-many-locals
    def write(self, db_name: str, measurement: str, columns: list, values: list):
        """
        Write fields and tags.

        :param db_name:
        :param measurement:
        :param columns:
        :param values:
        :return:
        """
        tag_keys = self.get_measurement_tag_keys(db_name, measurement)
        fields_types = self.get_measurement_fields_types(db_name, measurement)
        dict_values = {pair[0]: pair[1] for pair in zip(columns, values)}
        tags = []
        for tag_key in tag_keys:
            tag_value = dict_values.pop(tag_key)
            if not tag_value:
                continue
            tags.append(f"{tag_key}={tag_value}")

        # '2022-02-07T17:29:44.72004Z'
        date_time = datetime.datetime.strptime(dict_values.pop("time"), "%Y-%m-%dT%H:%M:%S.%f%z")
        timestamp = int(date_time.timestamp()*1000000000)

        fields = []
        for field_key, value in dict_values.items():
            if not value:
                continue
            fields.append(self.field_value_to_str(field_key, value, fields_types=fields_types))

        str_data = f"{measurement},{','.join(tags)} {','.join(fields)} {timestamp}"
        ret = self.post(f"write?db={db_name}", str_data)
        logger.info(ret)
        return ret

    # pylint: disable= too-many-locals, too-many-arguments
    def write_batch(self, db_name: str, measurement: str, columns: list, lst_values: list, force_cast=False):
        """
        Write fields and tags.

        :param force_cast:
        :param db_name:
        :param measurement:
        :param columns:
        :param lst_values:
        :return:
        """
        lst_data = []
        tag_keys = self.get_measurement_tag_keys(db_name, measurement)
        fields_types = self.get_measurement_fields_types(db_name, measurement)

        for values in lst_values:
            dict_values = {pair[0]: pair[1] for pair in zip(columns, values)}
            tags = []
            for tag_key in tag_keys:
                try:
                    tag_value = dict_values.pop(tag_key)
                except KeyError:
                    continue

                if not tag_value:
                    continue
                tags.append(f"{tag_key}={tag_value}")

            # '2022-02-07T17:29:44.72004Z'
            time_field = dict_values.pop("time")
            try:
                strip_time, subsecond = time_field.split(".")
            except ValueError as exception_instance:
                # 2023-01-26T02:55:00Z
                # 2023-02-02T03:06:14Z
                if not time_field[-4] != ":":
                    raise ValueError(time_field) from exception_instance
                strip_time = time_field[:-1]
                subsecond = "000000000Z"

            date_time = datetime.datetime.strptime(strip_time, "%Y-%m-%dT%H:%M:%S")
            if not subsecond.endswith("Z"):
                raise RuntimeError(subsecond)

            subsecond = subsecond[:-1]
            subsecond_int = int(subsecond) * (10**(9-len(subsecond)))
            # date_time = datetime.datetime.strptime(strip_time, "%Y-%m-%dT%H:%M:%S.%f%z")
            timestamp = int(date_time.timestamp()*1000000000)
            timestamp += subsecond_int

            fields = []
            for field_key, value in dict_values.items():
                if not value:
                    continue

                if force_cast:
                    value = fields_types[field_key](value)

                fields.append(self.field_value_to_str(field_key, value, fields_types=fields_types))

            str_data = f"{measurement},{','.join(tags)} {','.join(fields)} {timestamp}"
            lst_data.append(str_data)
        ret = self.post(f"write?db={db_name}", "\n".join(lst_data))
        logger.info(f"Total wrote count: {len(lst_data)}")
        return ret

    @staticmethod
    def backup_batch(file_path, db_name, measurement, columns, values):
        """
        Save data in a json file

        :param file_path:
        :param db_name:
        :param measurement:
        :param columns:
        :param values:
        :return:
        """
        dict_ret = {"db_name": db_name, "measurement": measurement, "columns": columns, "values": values}
        with open(file_path, "w", encoding="utf-8") as file_handler:
            json.dump(dict_ret, file_handler)

    def cast_measurement(self, src_db_name, db_name, measurement):
        """
        Rewrite all data.

        :param src_db_name:
        :param db_name:
        :param measurement:
        :return:
        """
        for measurement_series in self.yield_series(src_db_name, measurement):
            logger.info(f"Fetched data from '{measurement}'")
            start = datetime.datetime.now()
            self.write_batch(db_name, measurement, measurement_series["columns"],  measurement_series["values"],
                                   force_cast=True)
            logger.info(f"Wrote batch. Took: {datetime.datetime.now() - start}")

    def count_measurement(self, db_name, measurement):
        """
        Get count of all fields.

        :param db_name:
        :param measurement:
        :return:
        """
        response = self.get(f"query?db={db_name}&q=" + urllib.parse.quote_plus(
            f'SELECT count(*) FROM "{measurement}"'))

        return list(zip([column.lstrip("count_") for column in response["results"][0]["series"][0]["columns"][1:]]
                        , response["results"][0]["series"][0]["values"][0][1:]))

    def find_max_count(self, db_name, measurement):
        """
        Find maximum field count.

        :param db_name:
        :param measurement:
        :return:
        """
        ret = self.count_measurement(db_name, measurement)
        return max(ret, key=lambda x: x[1])
