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


def get_result_n_matches(n):
    pipeline = [{"$sort": {"match_time": -1}}, {"$project": {"_id": 0, "home_team": 1, "away_team": 1, "match_time": 1,
                                                             "score": 1, "probabilities": 1, "bets": 1}}, {"$limit": n}]
    matches = results.aggregate(pipeline)
    return matches

def get_fixture_n_matches(n):
    pipeline = [{"$sort": {"match_time": -1}}, {"$project": {"_id": 0, "home_team": 1, "away_team": 1, "match_time": 1,
                                                             "score": 1, "probabilities": 1, "bets": 1}}, {"$limit": n}]
    matches = fixtures.aggregate(pipeline)
    return matches

def calculate_bid(bid_type, bid_base, prob_success=0, odds_success=0):
    if bid_type == 'flat':
        return bid_base
    elif bid_type == 'kelly_crit':
        num = (prob_success+0.1)*odds_success - 1
        denom = odds_success - 1
        return num/denom*bid_base

def get_last_n_matches_for_plot(n, bid_base, bid_type):
    pipeline = [{"$sort": {"match_time": -1}}, {"$project": {"_id": 0, "home_team": 1, "away_team": 1, "match_time": 1,
                                                             "score": 1, "probabilities": 1, "bets": 1}}, {"$limit": n}]
    matches = col.aggregate(pipeline)
    X = [i + 1 for i in range(n)]
    Y = [0]
    cash = 0
    text = []
    for item in matches:
        _bid = 0
        _gain = 0
        if item['probabilities'][0]['prediction'] == "HOME":
            _bid = calculate_bid(bid_type, bid_base, item['probabilities'][0]['p1'], item["bets"][0]["bet_home"])
            if item['probabilities'][0]['prediction'] == item['score']['result']:
                _gain = item["bet"]["bet_home"] * _bid
            else:
                _gain = 0 - _bid
        elif item['probabilities'][0]['prediction'] == "AWAY":
            _bid = calculate_bid(bid_type, bid_base, item['probabilities'][0]['p2'], item["bets"][0]["bet_away"])
            if item['probabilities'][0]['prediction'] == item['score']['result']:
                _gain = item["bet"]["bet_away"] * _bid
            else:
                _gain = 0 - _bid
        elif item['probabilities'][0]['prediction'] == "DRAW":
            _bid = calculate_bid(bid_type, bid_base, item['probabilities'][0]['pX'], item["bets"][0]["bet_draw"])
            if item['probabilities'][0]['prediction'] == item['score']['result']:
                _gain = item["bet"]["bet_draw"] * _bid
            else:
                _gain = 0 - _bid
        elif item['probabilities'][0]['prediction'] == "SKIP":
            pass
        cash += _gain

        Y.append(cash)
        text.append("{}<br>{} - {} [{}-{}]<br>Prediction: {} Result: {}<br>Bid: {}<br>Gain/loss: {}"
                    .format(item['match_time'], item['home_team'], item['away_team'], item['score']['score_home'],
                            item['score']['score_away'], item['probabilities'][0]['prediction'],
                            item['score']['result'], _bid, _gain))

    return X, Y, text

if __name__ == '__main__':
    get_last_n_matches_for_plot(10, 100, 'kelly_crit')
