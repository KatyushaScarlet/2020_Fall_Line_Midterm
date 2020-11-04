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
        self.time = None

class OrderRequestMode():
    def __init__(self):
        self.userid = None
        self.spotid = None
        self.count = None

class OrderModel():
    def __init__(self):
        self.id = None
        self.user = None
        self.spot = None
        self.count = None
        self.datetime = None