

def handler(event, context):
    print("Done")
    return {"statusCode": 200, "body": str(event) + str(context)}
