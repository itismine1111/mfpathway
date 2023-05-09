__author__ = 'Soumendu Mukherjee'

def make_dict(code,status,message):
    return {'code': code, 'status': status, 'message':message}

SUCCESSFUL_OPERATION = make_dict(0,'success','success')
INVALID_PARAMETER = make_dict(1, 'error', "INVALID PARAMETER")
UNAUTHENTICATED = make_dict(12,'success','success')

