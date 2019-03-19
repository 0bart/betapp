from app import app

with open('config.json') as file_conf:
    conf = json.load(file_conf)

db_string = 'mongodb://{}:{}@{}:{}'.format(conf['mongo']['user'], conf['mongo']['pwd'], conf['mongo']['host'], conf['mongo']['port'])

client = pymongo.MongoClient(db_string)
matches = client.matches.betMatches

@app.route('/')
@app.route('/index')
def index():
    matches_ = matches.aggregate(['$match': {'prediction': {"$eq": "score.result"}}])
    return 
