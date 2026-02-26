from dataclasses import dataclass

@dataclass
class Match:
	teams: list[str]
	scores: list[int]

	def render(self, rn: int, mn: int, bo: int=3):
		return f'''|R{rn}M{mn}={{{{Match
	|date=|bestof={bo}
	|opponent1={{{{TeamOpponent|template={self.teams[0]}|score={self.scores[0]}}}}}
	|opponent2={{{{TeamOpponent|template={self.teams[1]}|score={self.scores[1]}}}}}
}}}}
'''

def render_double_elim(upper, lower):
	total_rounds = len(lower) + 1

	text = ''

	for rnd in range(1, total_rounds + 1):
		r_upper = []
		if rnd == 1:
			r_upper = upper[0]
		elif rnd == total_rounds:
			r_upper = upper[len(r_upper) - 1]
		elif rnd % 2 == 0:
			r_upper = upper[rnd // 2]
		
		r_lower = lower[rnd-1] if rnd < total_rounds else []

		for i, match in enumerate([*r_upper, *r_lower]):
			text += match.render(rnd, i+1)

	return text