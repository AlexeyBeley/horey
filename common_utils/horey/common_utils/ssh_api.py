"""
SSH tools
"""
from horey.common_utils.bash_executor import BashExecutor


class SSHAPI:
    """
    Main class
    """

    @staticmethod
    def generate_ed25519_key(owner_email, output_file_path):
        """
        Generate key using bash and ssh-keygen

        :param owner_email:
        :param output_file_path:
        :return:
        """

        command = f'ssh-keygen -t ed25519 -C "{owner_email}" -f {output_file_path}'
        ret = BashExecutor.run_bash(command)
        breakpoint()
        return ret
