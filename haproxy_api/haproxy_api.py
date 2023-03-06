"""
Simple parser.

"""
#!/usr/bin/python3
import sys


class HAProxyAPI:
    """
    Simple output parser.

    """

    @staticmethod
    def parse_output(file_path):
        """
        srv_op_state: Server operational state (UP/DOWN/...).
        0 = SRV_ST_STOPPED - The server is down.
        1 = SRV_ST_STARTING - The server is warming up (up but throttled).
        2 = SRV_ST_RUNNING - The server is fully up.
        3 = SRV_ST_STOPPING - The server is up but soft-stopping (eg: 404).
        :param file_path:
        :return:
        """
        with open(file_path, encoding="utf-8") as file_reader:
            lines = [line.strip() for line in file_reader.readlines()]
            if lines[0].startswith("# "):
                lines[0] = lines[0][2:]
        if len(lines) != 2:
            raise RuntimeError(lines)

        for pair in zip(lines[0].split(" "), lines[1].split(" ")):
            print(pair)


_file_path = sys.argv[1]
HAProxyAPI.parse_output(_file_path)
