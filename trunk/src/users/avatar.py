from database import interfaces as idb

class Avatar(object):
    
    def __init__(self, creds, store):
        self.creds = creds
        self.topics = idb.ITopicsDatabase(store)
        self.sections = idb.ISectionsDatabase(store)
        self.users = idb.IUsersDatabase(store)
        self.store = store
        
