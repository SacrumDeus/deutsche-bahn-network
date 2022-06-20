
#===============================
# Required pacakges
#===============================

from neo4j import GraphDatabase
import pandas as pd



#===============================
# Neo4j Connection Class
#===============================

# class for connecting to an neo4j database and queried data

# copied from https://towardsdatascience.com/neo4j-cypher-python-7a919a372be7 with three modifications

class Neo4jConnection:
    

    def __init__(self, uri, user, pwd, db):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None

        # modification 1 - database variable
        self.__db = db
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, db=None, returnDataFrame = True):
        
        # modification 2 - use db which was set during initialization
        if db == None:
            db = self.__db

        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally: 
            if session is not None:
                session.close()
        
        # modification 3 - convert to pandas data frame, if required
        if returnDataFrame == True:
            response = [x.data() for x in response]
            response = pd.DataFrame(response)

        return response