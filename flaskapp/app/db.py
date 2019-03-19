import json
import pymongo
from app import app

with app.open_resource('config.json') as file_conf:
    conf = json.load(file_conf)

db_string = 'mongodb://{}:{}@{}:{}'.format(conf['mongo']['user'], conf['mongo']['pwd'],
                                           conf['mongo']['host'], conf['mongo']['port'])

client = pymongo.MongoClient(db_string)
col = client.matches.betMatches


def get_last_n_matches(n):
    pipeline = [{"$sort": {"match_time": -1}}, {"$project": {"_id": 0, "home_team": 1, "away_team": 1, "match_time": 1,
                                                             "score": 1, "prediction": 1, "bet": 1}}, {"$limit": n}]
    matches = col.aggregate(pipeline)
    return matches
