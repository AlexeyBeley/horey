from system_function_common import SystemFunctionCommon

import argparse
import pdb


class Check(SystemFunctionCommon):
    def __init__(self):
        super().__init__()

    def check_swap_size(self, swap_size=None):
        """
        #collect
        #swapon --show

        #output
        #NAME       TYPE   SIZE USED PRIO
        #/swapfile  file 1024M   0B   -2
        @param kwargs:
        @return:
        """
        ret = self.run_bash("swapon --show")
        lines = ret.split("\n")
        header_vars = ["NAME", "TYPE", "SIZE", "USED", "PRIO"]
        for header_var in header_vars:
            if header_var not in lines[0]:
                raise RuntimeError(f"Wrong output of 'swapon --show': {ret}")
        for line in lines[1:]:
            if line.startswith("/swapfile"):
                while "  " in line:
                    line = line.replace("  ", " ")
                _filename, _type, size, _used_size, _prio = line.split(" ")

                if size.endswith("G"):
                    size = size[:-1]
                else:
                    raise RuntimeError(size)
                if size == str(swap_size):
                    return True
                break
        raise RuntimeError(f"'swapon --show' output: {ret}")

        file_content = "vm.swappiness=1"
        ret = self.run_bash(f"cat /etc/sysctl.conf | grep {file_content}")
        if ret != file_content:
            raise RuntimeError(f"can not find {file_content} in /etc/sysctl.conf: {ret}")


# region check_swappiness
def check_swappiness_parser():
    description = "check_swappiness"
    parser = argparse.ArgumentParser(description=description)
    parser.epilog = f"Usage: python3 {__file__} [options]"
    return parser


def check_swappiness(arguments) -> None:
    Check().check_swappiness()


SystemFunctionCommon.ACTION_MANAGER.register_action("check_swappiness", check_swappiness_parser, check_swappiness)
# endregion


if __name__ == "__main__":
    SystemFunctionCommon.ACTION_MANAGER.call_action()

