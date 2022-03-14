import urllib3


def str2bool(v):
    '''Retorna un Boolean a partir de un palabra que se encuentre en la lista'''
    return v.lower() in ("yes", "true", "t", "1")


def field_in_dict(dictionary, field):
    if field in dictionary:
        return True
    return False


def get_response_body(code=200, message='OK', user_message='', body=None):
    if code == 200:
        return {'code':200, 'message':message, 'user_message':user_message, 'body':body}
    return {'error':{'code':code, 'message':message, 'user_message':user_message}}

def invoke_api(url, body, headers={'Content-Type': 'application/json'}, method='POST'):
    http = urllib3.PoolManager()
    response = http.request(method,
                            url,
                            body=body,
                            headers=headers)
    return response