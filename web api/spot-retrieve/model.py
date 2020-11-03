class ResponseModel():
    def __init__(self):
        self.status = -1
        self.result = None
 
class UserModel():
    def __init__(self):
        self.name = None
        self.phone = None
        self.email = None
        self.lineId = None
        self.role = "customer"

class SpotModel():
    def __init__(self):
        self.id = None
        self.name = None
        self.description = None
        self.detail = None
        self.phone = None
        self.address = None
        self.zipcode = None
        self.city = None
        self.town = None
        self.ticket = None
        self.remark = None

class QueryModel():
    def __init__(self):
        self.id = None
        self.name = None
        self.address = None