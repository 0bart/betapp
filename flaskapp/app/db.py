import json
import pymongo
from app import app

with app.open_resource('config.json') as file_conf:
    conf = json.load(file_conf)

db_string = 'mongodb://{}:{}@{}:{}'.format(conf['mongo']['user'], conf['mongo']['pwd'],
                                           conf['mongo']['host'], conf['mongo']['port'])

client = pymongo.MongoClient(db_string)
fixtures = client.betapp.fixtures
results = client.betapp.results

def get_fixture_n_matches(n):
    pipeline = [{"$sort": {"match_time": -1}}, {"$project": {"_id": 0, "home_team": 1, "away_team": 1, "match_time": 1,
                                                             "score": 1, "probabilities": 1, "bets": 1,
                                                             "last_updated": 1}}, {"$limit": n}]
    matches = fixtures.aggregate(pipeline)
    return matches

def get_result_n_matches(n):
    pipeline = [{"$sort": {"match_time": -1}}, {"$project": {"_id": 0, "home_team": 1, "away_team": 1, "match_time": 1,
                                                             "score": 1, "probabilities": 1, "bets": 1}}, {"$limit": n}]
    matches = results.aggregate(pipeline)
    return matches

if __name__ == '__main__':
    get_last_n_matches_for_plot(10, 100, 'kelly_crit')
