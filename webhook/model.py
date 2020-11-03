class DialogflowModel():
    def __init__(self):
        self.eventName = None
        self.actionName = None
        self.queryInput = None
        self.parameters = {}
        self.responses = []
        self.lineId: None

 
class UserModel():
    def __init__(self):
        self.name = None
        self.phone = None
        self.email = None
        self.lineId = None
        self.role = "customer"


