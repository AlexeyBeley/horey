"""
AWS lambda client to handle lambda service API requests.
"""
from horey.aws_api.aws_clients.boto3_client import Boto3Client

from horey.aws_api.base_entities.aws_account import AWSAccount
from horey.aws_api.aws_services_entities.stepfunctions_state_machine import StepfunctionsStateMachine

from horey.h_logger import get_logger

logger = get_logger()


class StepfunctionsClient(Boto3Client):
    """
    Client to handle specific aws service API calls.
    """

    def __init__(self):
        """
        list_activities = list(self.execute(self.get_session_client(region=region).list_activities, None, raw_data=True))
        # list_executions = list(self.execute(self.get_session_client(region=region).list_executions, None, raw_data=True))
        # list_map_runs = list(self.execute(self.get_session_client(region=region).list_map_runs, None, raw_data=True))
        list_state_machines = list(self.execute(self.get_session_client(region=region).list_state_machines, None, raw_data=True))
        # list_tags_for_resource = list(self.execute(self.get_session_client(region=region).list_tags_for_resource, None, raw_data=True))

        """
        client_name = "stepfunctions"
        super().__init__(client_name)

    def get_all_state_machines(self, region=None, full_information=True):
        """
        Get all state_machines in all regions.
        :return:
        """

        if region is not None:
            return self.get_region_state_machines(
                region, full_information=full_information
            )

        final_result = []
        for _region in AWSAccount.get_aws_account().regions.values():
            final_result += self.get_region_state_machines(
                _region, full_information=full_information
            )

        return final_result

    def get_region_state_machines(self, region, full_information=True):
        """
        Region specific state machines.

        :param region:
        :param full_information:
        :return:
        """

        final_result = []
        for dict_src in self.execute(
                self.get_session_client(region=region).list_state_machines, "stateMachines"
        ):
            obj = StepfunctionsStateMachine(dict_src)
            final_result.append(obj)
            if full_information:
                self.update_state_machine_info(obj)

        return final_result

    def update_state_machine_info(self, obj):
        """
        Update current status.

        :param obj:
        :return:
        """

        for dict_src in self.execute(
                self.get_session_client(region=obj.region).describe_state_machine, None, raw_data=True,
                filters_req={"stateMachineArn": obj.arn}
        ):
            del dict_src["ResponseMetadata"]
            obj.update_from_raw_response(dict_src)

    def provision_state_machine(self, state_machine: StepfunctionsStateMachine):
        """
        Provision from object.

        :param state_machine:
        :return:
        """

        region_state_machines = self.get_region_state_machines(
            state_machine.region
        )
        for region_state_machine in region_state_machines:
            if (
                    region_state_machine.name == state_machine.name
            ):
                state_machine.update_from_raw_response(
                    region_state_machine.dict_src
                )
                return
        response = self.provision_state_machine_raw(state_machine.region,
                                                    state_machine.generate_create_request()
                                                    )
        state_machine.update_from_raw_response(response)

    def provision_state_machine_raw(self, region, request_dict):
        """
        Provision from raw request.

        :param request_dict:
        :return:
        """

        logger.info(f"Creating state_machine: {request_dict}")
        for response in self.execute(
                self.get_session_client(region=region).create_state_machine,
                None,
                raw_data=True,
                filters_req=request_dict,
        ):
            del response["ResponseMetadata"]
            return response
