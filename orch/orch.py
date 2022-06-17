import urllib3

url = 'https://pyasz7b5kl.execute-api.us-east-1.amazonaws.com/dev/all'
# turn into a list when we have multiple urls

def orch(event, context):

    http = urllib3.PoolManager()
    res = http.request('GET', url)

    body = res.data.decode('utf-8')

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            'Access-Control-Allow-Credentials': True
        },
        "body": body
    }

    return response


# note: with multiple adapter outputs, want to put together the sections, not have 
# a list of json bodies (kinda like stack each section)