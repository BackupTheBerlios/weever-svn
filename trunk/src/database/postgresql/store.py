from twisted.enterprise import adbapi
from twisted.python import components

class Store(object):

    def __init__(self, db_adapter, database, user, password):
        self.__pool = adbapi.ConnectionPool(db_adapter,
                                            database=database,
                                            user=user, password=password)

    def runQuery(self, query, *args):
        d = self.__pool.runInteraction(self.mapQuery, query, args)
        return d

    def mapQuery(self, curs, query, *args):
        curs.execute(query, *args)
        result = curs.fetchall()
        columns = [d[0] for d in curs.description]
        return [dict(zip(columns, r)) for r in result]

    
