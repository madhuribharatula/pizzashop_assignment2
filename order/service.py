import boto3
import datetime

selection_msg = 'please choose one of these Selection'
size_msg = 'Which size do you want?'


dynamodb = boto3.resource('dynamodb', region_name='region', endpoint_url="DB endpoint",
aws_access_key_id="access key",
aws_secret_access_key="secret key"
)


def pizza_order_handler(event,context):

    http_method = event['httpMethod']
    response = {}
    if http_method  == 'POST':
       response = create_handler(event,context)
    elif http_method == 'GET':
        response = view_handler(event,context)
    elif http_method == 'PUT':
        response = put_handler(event,context)
    return response




def create_handler(event, context):

    table=dynamodb.Table('order')
    #Create an order
    table.put_item(
          Item={
            'menu_id':event['menu_id'],
            'order_id':event['order_id'],
            'customer_name':event['customer_name'],
            'customer_email':event['customer_email'],
            'order_status': 'processing',
            "order": {
                 "selection": " ",
                 "size": " ",
                 "costs": " ",
                 "order_time": " "
               }
           })
    menu_table=dynamodb.Table('menu')
    menu_result=menu_table.get_item(
        Key={
            'menu_id':event['menu_id']
        })

    result=""
    try:
       var_selecion = menu_result['Item']['sequence'][0]
       result+="Hi "+event['customer_name']+" "
       val=1
       if var_selecion =='selection':
           result += selection_msg
       elif var_selecion =='size':
           result += size_msg

       for i in menu_result['Item'][var_selecion]:
          result+=(" "+str(val)+". "+str(i)+",")
          val+=1
       result=result[:-1]
       return {"Message": result}
    except KeyError:
         return "Incorrect menuid"
    except:
        return "No sequence Mentioned in the menu"


def put_handler(event,context):
    table=dynamodb.Table('order')
    menu_table=dynamodb.Table('menu')
    order_id = event['params']['order_id']
    order_result = table.get_item(
        Key={
            "order_id": order_id
            }
    )
    menu_result=menu_table.get_item(
    Key={
            'menu_id':order_result['Item']['menu_id']
    })
    order_sequence = menu_result['Item']['sequence']

    message=''

    for seq in order_sequence:
        if order_result['Item']['order'][seq] == ' ':

            try:
               index_val = int(event['body']['input'])-1
               if index_val < len(menu_result['Item'][seq]):
                    update_value = menu_result['Item'][seq][int(index_val)]
                    if seq == 'size':
                        price = menu_result['Item']['price'][int(index_val)]
                        res=table.update_item(
                        Key={
                         'order_id':order_id
                        },
                        UpdateExpression= "SET #n.#d= :val1 , #n.costs = :val2",
                        ExpressionAttributeNames = {"#n":"order", "#d":seq},
                        ExpressionAttributeValues={':val1': update_value,
                                               ':val2':price})
                    else:
                        res=table.update_item(
                        Key={
                            'order_id':order_id
                        },
                        UpdateExpression= "SET #n.#d= :val1",
                        ExpressionAttributeNames = {"#n":"order", "#d":seq},
                        ExpressionAttributeValues={':val1': update_value})
                    break
               else:
                   return "Please choose from the available options"
            except:
                pass

    is_order_complete = True
    for seq in order_sequence:
        New_order_result = table.get_item(
        Key={
            "order_id": order_id
            }
        )
        if New_order_result['Item']['order'][seq] == ' ':
            is_order_complete = False
            if seq == 'selection':
                message += selection_msg
            else :
                message += size_msg
            val=1
            for i in menu_result['Item'][seq]:
                message+=(" "+str(val)+". "+str(i)+",")
                val+=1
            message=message[:-1]
            return {"Message":message}

    if is_order_complete:
        t_time = str(datetime.datetime.now().strftime('%m-%d-%Y@%H:%M:%S'))
        neworder_result = table.get_item(
        Key={
            "order_id": order_id
            }
        )
        price = neworder_result['Item']['order']['costs']
        res=table.update_item(
           Key={
             'order_id': order_id
            },
           UpdateExpression= "SET #n.order_time= :val1",
           ExpressionAttributeNames = {"#n":"order"},
           ExpressionAttributeValues={':val1':t_time})
        final_messsage = "Your order costs $"+price+". We will email you when the order is ready. Thank you!"
        return {"Message":final_messsage}


#view the order

def view_handler(event,context):
    table=dynamodb.Table('order')
    try:
        result = table.get_item(
            Key={
                "order_id": event.get("order_id")
            }
        )
        return result['Item']
    except KeyError:
        return "No order is placed with the given orderid"
