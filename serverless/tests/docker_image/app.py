"""
Echo function

"""


def handler(event, context):
    """
    Entrypoint

    :param event:
    :param context:
    :return:
    """
    print("Done")
    return {"statusCode": 200, "body": str(event) + str(context)}
