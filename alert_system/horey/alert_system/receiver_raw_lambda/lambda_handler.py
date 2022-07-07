import json
import os
import requests
from horey.slack_api.slack_api import SlackAPI
from horey.slack_api.slack_api_configuration_policy import SlackAPIConfigurationPolicy
from horey.slack_api.slack_message import SlackMessage

from horey.h_logger import get_logger

logger = get_logger()


def lambda_handler(event, context):
    """
    
    :param event:
    :param context:
    :return:
    """
    
    config = SlackAPIConfigurationPolicy()
    config.webhook_url = os.environ.get("SLACK_WEBHOOK")  
    slack_api = SlackAPI(configuration=config)
    message = SlackMessage(SlackMessage.Types.INFO)

    block = SlackMessage.HeaderBlock()
    block.text = "INFO: Merged to master"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "Component UI master was updated"
    message.add_block(block)

    block = SlackMessage.SectionBlock()
    block.text = "PR[2020]"
    block.link = "https://example.com"
    message.add_block(block)

    message.src_username = "slack_api"
    message.dst_channel = "#test"

    ret = slack_api.send_message(message)
    return {
        "statusCode": 200,
        "body": json.dumps(ret)
    }
    
    try:
        if len(event["Records"]) != 1:
            raise RuntimeError(event)

        message_text = event["Records"][0]["Sns"]["Message"]
        subject_text = event["Records"][0]["Sns"]["Subject"]
        if subject_text.startswith("Resolved") or subject_text.startswith("OK"):
            color_text = "#7CD197"
            icon_emoji_test = ":white_check_mark:"
        else:
            color_text = "danger"
            icon_emoji_test = ":bangbang:"
    except Exception:
        message_text = event
        subject_text = "No subject"
        color_text = "danger"
        icon_emoji_test = ":bangbang:"

    slack_data = {"text": subject_text,
                  "attachments": [{
                    "text": message_text,
                    "color": color_text,
                    }],
                  "channel": "#infra_team",
                  "username": "AWS SNS",
                  "icon_emoji": icon_emoji_test
                  }

    response = requests.post(
        webhook_url, data=json.dumps(slack_data),
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            f'Request to slack returned an error {response.status_code}, the response is:\n{response.text}'
        )

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
