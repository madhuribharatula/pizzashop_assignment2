import boto3


dynamodb = boto3.resource('dynamodb', region_name='Your region', endpoint_url="Dynamo db end point",
aws_access_key_id="acess key",
aws_secret_access_key="secret key"
)
table = dynamodb.Table('menu')

def pizza_menu_handler(event,context):

    http_method = event['httpMethod']
    response = {}
    if http_method  == 'POST':
       response = create_handler(event,context)
    elif http_method == 'GET':
        response = view_handler(event,context)
    elif http_method == 'PUT':
        response = put_handler(event,context)
    elif http_method == 'DELETE':
        response = delete_handler(event,context)
    return response


def create_handler(event, context):

    response = table.put_item(
    Item = {
        "menu_id" :  event['menu_id'],
        "store_name" : event['store_name'],
        "selection" : event['selection'],
        "size" : event['size'],
        "price" : event['price'],
        "store_hours" : event['store_hours'],
        "sequence" : event['sequence']
        }
    )

    return "OK"

def view_handler(event,context):
    try:
        result = table.get_item(
            Key={
                "menu_id": event.get("menu_id")
            }
        )
        return result['Item']
    except KeyError:
        return "Incorrect menuid"



def put_handler(event,context):
    menu_id = event['params']['menu_id']
    attributes = event['body'].keys()
    for k in attributes:
        if k!= 'menu_id':
            table.update_item(
                Key={
                'menu_id': menu_id
                },
                UpdateExpression= "set #n = :val",
                ExpressionAttributeNames = {"#n":k},
                ExpressionAttributeValues={ ':val' : event['body'][k] }
            )

    return "OK"


def delete_handler(event, context):

    table.delete_item(
        Key={
            "menu_id": event.get("menu_id")
        }
    )

    return "OK"
