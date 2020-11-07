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
        self.role = None
        self.password = None

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

class SpotRetrieveModel():
    def __init__(self):
        self.id = None
        self.name = None
        self.address = None

class OrderRetrieveModel():
    def __init__(self):
        self.orderid = None
        self.userid = None
        self.spotid = None

class OrderCreateModel():
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

class UserModel():
    def __init__(self):
        self.name = None
        self.phone = None
        self.email = None
        self.lineId = None
        self.role = None

class UserCheckModel():
    def __init__(self):
        self.lineId = None
        self.phone = None