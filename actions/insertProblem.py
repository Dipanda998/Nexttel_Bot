from pymongo import MongoClient
import datetime
import pprint
client = MongoClient('localhost', 27017)
db = client.admin
collection = db.admin
posts = db.problemes 

def probleme(nom,numero,probleme):
    post={
        'nom': nom,
        'numero': numero,
        'probleme':probleme,
        "date": datetime.datetime.utcnow()
    }
    
    result = posts.insert_one(post).inserted_id

def verifier(numero,probleme):
    c=posts.count_documents({"$and":[ {"numero":numero}, {"probleme":probleme}]})
    return c

def recuperer(type):
    posts = db.forfait
    for post in posts.find({"type":type}):
          return post['phrase']
