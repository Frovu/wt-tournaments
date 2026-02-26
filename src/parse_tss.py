import requests

from brackets import Match, render_double_elim

TSS_API = 'https://tss.warthunder.com/functions.php'

def parse_match(data):
	teams =  [data["realNameA"], data["realNameB"]]
	scores = [int(data["scoreA"]), int(data["scoreB"])]

	return Match(teams, scores)

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

	upper = [[parse_match(mt) for mt in rnd] for rnd in upper if len(rnd) <= truncate]
	lower = [[parse_match(mt) for mt in rnd] for rnd in lower if len(rnd) <= truncate / 2]

	return upper, lower

def test():
	text = render_double_elim(*fetch_bracket(24019))
	with open('out.txt', 'w') as f:
		f.write(text)

test()