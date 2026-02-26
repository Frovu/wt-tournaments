import requests
from datetime import datetime, timezone

from brackets import Match, render_double_elim

TSS_API = 'https://tss.warthunder.com/functions.php'

def fetch_game_match_winners(tournament_id: int, match_id: int, total_score: dict[str, int], type_bracket: str):
	print(f'fetching match {match_id} results ({":".join(list(total_score.keys()))})')
	res = requests.post(TSS_API, {
		"tournamentID": str(tournament_id),
		"idMatch": str(match_id),
		"typeMatch": type_bracket,
		"action": "tournamentInfoAll"
	})

	if res.status_code != 200:
		raise Exception(f'Failed fetching match results: {match_id}')
	
	data = res.json()
	games = data['data']['matchResults'][str(match_id)]
	team1, team2 = list(total_score.keys())
	match_winner = team1 if total_score[team1] > total_score[team2] else team2

	results = ["" for g in games]
	results[-1] = match_winner

	# collect sum of deaths squared for each team for each game except last one
	deaths_metrics = []
	for game in games[:-1]:
		deaths_metric = {
			team1: 0,
			team2: 0
		}
		for player in game:
			team = player["teamName"]
			deaths = player["values"]["DEATH"]
			deaths_metric[team] += deaths ** 2
		deaths_metrics.append(deaths_metric)

	# first look at the games with biggest difference between death totals
	metrics_diffs = [abs(m[team1] - m[team2]) for m in deaths_metrics]
	sorted_idxs = [p[0] for p in sorted(enumerate(metrics_diffs), key=lambda x: x[1])][::-1]

	accounted = {
		team1: 0,
		team2: 0
	}
	accounted[match_winner] = 1

	for i in sorted_idxs:
		metrics = deaths_metrics[i]
		game_winnner = team1 if metrics[team1] < metrics[team2] else team2
		results[i] = game_winnner
		print('solving winner', i, results)
		accounted[game_winnner] += 1

		# set reamining games winner to other team
		if accounted[team1] == total_score[team1]:
			for i, val in enumerate(results):
				if not val:
					results[i] = team2
			break
		elif accounted[team2] == total_score[team2]:
			for i, val in enumerate(results):
				if not val:
					results[i] = team1
			break

	return results

def fetch_match_info(tournament_id: int, match_id: int):
	print(f'fetching match {match_id} info')
	res = requests.get(TSS_API, {
		"tournamentID": str(tournament_id),
		"idMatch": str(match_id),
		"action": "getInfoMatch"
	})

	if res.status_code != 200:
		raise Exception(f'Failed fetching match results: {match_id}')
	
	data = res.json()
	data = data["data"]

	start_ts = data["allBattleTime"][0]["timeStart"]
	time = datetime.fromtimestamp(start_ts, tz=timezone.utc)

	map_key = data["matchParametrs"]["mission"][0]["key"]
	
	return time, map_key

def parse_match(tournament_id: int, data: dict):
	teams: list[str] = [data["realNameA"], data["realNameB"]]
	scores = [int(data["scoreA"]), int(data["scoreB"])]
	type_bracket = data["typeBracket"]
	match_id = int(data["id"])

	if scores[0] == 0:
		results = [teams[1]] * scores[1]
	elif scores[1] == 0:
		results = [teams[0]] * scores[0]
	else:
		dscores = dict(zip(teams, scores))
		results = fetch_game_match_winners(tournament_id, match_id, dscores, type_bracket)

	time, map_name = fetch_match_info(tournament_id, match_id)

	return Match(time, teams, results, map_name)

def fetch_bracket(tournament_id: int, truncate=16):
	res = requests.post(TSS_API, {
		"tournamentID": str(tournament_id),
		"action": "GetArrayBracketData"
	})

	if res.status_code != 200:
		raise Exception('Failed fetching tournament data')
	
	data = res.json()
	data = data['data']['bracket']

	upper = [ *data['winner']['Winner'], *data['winner']['Final'] ]
	lower = [ *data['loser']['Looser'], *data['loser']['LooserFinal'], *data['loser']['Semifinal'] ]

	upper = [[parse_match(tournament_id, mt) for mt in rnd] for rnd in upper if len(rnd) <= truncate]
	lower = [[parse_match(tournament_id, mt) for mt in rnd] for rnd in lower if len(rnd) <= truncate / 2]

	return upper, lower

def test():
	text = render_double_elim(24019, *fetch_bracket(24019, truncate=16))
	with open('out.txt', 'w') as f:
		f.write(text)

test()