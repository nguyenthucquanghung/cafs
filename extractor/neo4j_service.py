from py2neo import Graph, Node


NEO4J_URL = "http://localhost:7474/"
graph = Graph(NEO4J_URL, auth=("neo4j", "1"))


def createBN(idBN, name=None, age=None, origin=None, date_positive=None,
            last_update=None, status="alive",
            sex=None, country=None):
    BN = Node("BN", id=str(idBN), name=name, age=age,
            origin=origin, date_positive=date_positive,
            last_update=last_update, status=status,
            sex=sex, country=country)
    try:
        tx = graph.begin()
        tx.create(BN)
        tx.commit()
    except Exception as e:
        print(e)


def updateBN(BNid, type, value):
    command = """
    MATCH (a:BN)
    WHERE a.id = "%s"
    SET a.%s = "%s"
    """ % (BNid, type, value)
    try:
        graph.run(command)
    except Exception as e:
        print(e)


def getNodeBN(idBN):
    return graph.nodes.match("BN",id=idBN)


def createConnect(idBN1, relation, idBN2=None):
    command = """
    MATCH (a:BN),(b:BN)
    WHERE a.id = "%s" and  b.id = "%s"
    merge (a)-[r:QUAN_HỆ {roles: "%s"}]->(b)
    return a,b
    LIMIT 50""" % (idBN1, idBN2, relation)
    try:
        graph.run(command)
    except Exception as e:
        print(e)


def checkExist(node_label, id):
    command = """
    MATCH (a:%s)
    WHERE a.id = "%s"
    return a """ % (node_label, id)


def createTranspotation(idBN, transpotation):
    command = """
    MERGE (a:PTVT {id:"%s"})""" % (transpotation)
    try:
        graph.run(command)
    except Exception as e:
        print(e)
    command = """
    MATCH (a:BN), (b:PTVT)
    WHERE a.id = "%s" and  b.id = "%s"
    merge (a)-[r:TỪNG_SỬ_DỤNG]->(b)
    return a,b
    LIMIT 50""" % (idBN, transpotation)
    try:
        graph.run(command)
    except Exception as e:
        print(e)


def createConnectPTVT(idBN1, relation, idBN2=None):
    command = """
    MATCH (a)-[r:TỪNG_SỬ_DỤNG]->(b)
    WHERE a.id = "%s" and  b.id = "%s"
    DELETE r
    """ % (idBN1, idBN2)
    try:
        graph.run(command)
    except Exception as e:
        print("Error: ",e)
    command = """
    MATCH (a:BN), (b:PTVT)
    WHERE a.id = "%s" and  b.id = "%s"
    merge (a)-[r:TỪNG_SỬ_DỤNG {roles: "%s"}]->(b)
    return a,b
    LIMIT 50""" % (idBN1, idBN2, relation)
    try:
        graph.run(command)
    except Exception as e:
        print("Error: ",e)


def getInfoBN(BNid, type):
    command = """
    MATCH (a:BN)
    WHERE a.id = "%s"
    return a.%s
    """ % (BNid, type)
    # print(command)
    try:
        ret = graph.run(command)
        # if len(ret.data()) == 0:
        #     return None
        data = ret.data()[0]
        return (data["a."+type])
    except Exception as e:
        return None


def getTranspotation(idBN):
    command = """
    MATCH (n1)-[r]->(n2:PTVT) Where n1.id="%s" RETURN n2.id
    """ % (idBN)
    try:
        ret = graph.run(command)
        data = ret.data()[0]
        return (data["n2.id"])
    except Exception as e:
        return None


def getRelationBN(idBN1, idBN2):
    command = """
    MATCH (n1)-[r]->(n2) Where n1.id="%s" and n2.id="%s" RETURN r.roles
    """ % (idBN1,idBN2 )
    try:
        ret = graph.run(command)
        data = ret.data()[0]
        return (data['r.roles'])
    except Exception as e:
        return None


