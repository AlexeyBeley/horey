from lambda_test_2 import output_text


def lambda_handler(event, context):
    """
    :param event:
    :param context:
    :return:
    """
    print(output_text)
    return "200"
