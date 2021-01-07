"""
Some reusable stuff.
"""
import datetime


class CommonUtils:
    """
    Some stuff to be reused
    """
    @staticmethod
    def find_objects_by_values(objects, values, max_count=None):
        """
        Find objects with all specified values.
        If no such attr: do not add to the return list

        :param objects: list of objects
        :param values: dict of key - value
        :param max_count: Maximum amount to return
        :return:
        """

        objects_ret = []
        for obj in objects:
            for key, value in values.items():
                try:
                    if getattr(obj, key) != value:
                        break
                except AttributeError:
                    break
            else:
                objects_ret.append(obj)
                if max_count is not None and len(objects_ret) >= max_count:
                    break

        return objects_ret

    @staticmethod
    def int_to_str(number):
        """
        Int to comma separated string
        :param number:
        :return:
        """
        if not isinstance(number, int):
            raise ValueError(number)

        str_ret = '{:,}'.format(number)

        return str_ret

    @staticmethod
    def bytes_to_str(number):
        """
        Pretty print of storage
        :param number:
        :return:
        """
        if not isinstance(number, int):
            raise ValueError(number)

        if number < 0:
            raise ValueError(number)

        if number == 0:
            return "0"

        mapping = {
                    1: "Bytes",
                    1024: "KiB",
                    1024 ** 2: "MiB",
                    1024 ** 3: "GiB",
                    1024 ** 4: "TiB",
                    1024 ** 5: "PiB"
        }

        key_limit = 1

        for key_limit_tmp, _ in mapping.items():
            if number < key_limit_tmp:
                break
            key_limit = key_limit_tmp
        quotient, remainder = divmod(number, key_limit)
        int_percent_reminder = round((remainder/key_limit)*100)
        if int_percent_reminder == 0:
            return_number = str(quotient)
        else:
            float_result = float(f"{quotient}.{int_percent_reminder}")
            return_number = str(round(float_result, 2))
        return f"{return_number} {mapping[key_limit]}"

    @staticmethod
    def timestamp_to_datetime(timestamp):
        """
        int to datetime.
        :param timestamp:
        :return:
        """
        return datetime.datetime.fromtimestamp(timestamp)
