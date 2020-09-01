import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    '''
    Helper class to convert a DynamoDB item to JSON.
    '''
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        if isinstance(o, set):  #<---resolving sets as lists
            return list(o)
        return super(DecimalEncoder, self).default(o)