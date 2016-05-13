# How to use vk package:
# import vk
# app_id, token = '4871635', '...'
# vksession = vk.Session(access_token=token)
# vkapi = vk.API(vksession)
# vkapi.func(**params)

import time

def get_all_messages_from(vkapi, user_id, is_chat=True):
    
    """Fetches all messages from user conversation or group chat.

    Takes: vkapi - vk api interface from vk package, 
           user_id.
           If is_chat is True, user_id is treated as chat_id
    Returns: list of message objects (dicts)"""
    
    messages_gethistory_params = {
        'offset': '0',
        'count': '200',
        'user_id': str(user_id),
        'rev': '1'
    }
    
    all_messages = []
    current_bulk = ["placeholder"]
    n = 0
    
    total = (vkapi.messages.getHistory(chat_id=messages_gethistory_params["user_id"],count=0) 
             if is_chat 
             else vkapi.messages.getHistory(user_id=messages_gethistory_params["user_id"],count=0))[0]
    print("Going to fetch %d messages" % total)
    
    while True:
        msg_query_part = """API.messages.getHistory({"offset": %d, "count": 200, """ + (""""user_id" """ if not is_chat else """"chat_id" """) + """: %d, "rev": %d})+"""
        msg_query = "return "
        for i in range(n,n+4000,200):
            msg_query += msg_query_part % (i, 
                                           int(messages_gethistory_params['user_id']), 
                                           int(messages_gethistory_params['rev']))
        msg_query = msg_query.strip("+")
        msg_query += ";"
        
        current_bulk = vkapi.execute(code=msg_query)
        time.sleep(1)
        
        all_messages.append(current_bulk)
        n += len(current_bulk)
        if type(current_bulk[-1]) is int:
            break
        
        print("Inserted %d elements.\nlast: %s" % (n,all_messages[-1][-1]))
        
    flat = [y for x in all_messages for y in x]
    cleaned = [x for x in flat if type(x) is not int]  
    return cleaned


def get_user(vkapi,id):
    """Wrapper for users.get call
    Takes user id, returns user object with name and screen_name"""
    time.sleep(1)
    return vkapi.users.get(
        user_ids=str(id),
        fields='name,screen_name')


def construct_user_set_from_data(vkapi,data):
    """Takes vk api object, data produced by get_all_messages_from
    Returns list of unique tuples (first_name,last_name,link,deactivation_status), sorted by deactivation_status"""

    user_set = set(dataitem['uid'] for dataitem in data)
    user_data = [get_user(vkapi, u)[0] for u in user_set]
    
    user_tuples = []

    for u in sorted(user_data,key=lambda x: 'deactivated' in x):
        try:
            user_tuples.append((u['first_name'],u['last_name'],"http://vk.com/" + u['screen_name']))
        except KeyError:
            user_tuples.append((u['first_name'],u['last_name'],"http://vk.com/id" + str(u['uid']),u['deactivated']))
    return user_tuples