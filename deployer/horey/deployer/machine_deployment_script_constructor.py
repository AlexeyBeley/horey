import pdb
import os

class MachineDeploymentScriptConstructor:
    def __init__(self, script_file_path):
        self.script_file_path = script_file_path
        self.init_script_file()

    def init_script_file(self):
        if not os.path.exists(self.script_file_path):
            with open(self.script_file_path, "w") as file_handler:
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "template_bash_script_file.sh")) as template_file_handler:
                    file_handler.write(template_file_handler.read())


    def add_module(self, module):
        pdb.set_trace()
