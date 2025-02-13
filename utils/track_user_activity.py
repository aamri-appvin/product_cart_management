from clickhouse_driver import Client
from datetime import datetime
from schema import User_Info

client = Client(host='localhost', port=9000,database="user_analytics")

def log_user_activity(user: User_Info):
    query = '''
    INSERT INTO user_activity(user_id, action, product_id, timestamp)
    VALUES (%(user_id)s, %(action)s, %(product_id)s, %(timestamp)s)
    '''
    product_id = user.product_id if user.product_id is not None else 0
    data=[(user.user_id, user.action , product_id , datetime.utcnow())]

    client.execute(query, data)
    
    return {"data": "Successfully logged your data"}
#user-activity-analytics
#Most active users , no. of actions performed per hour , popular actions