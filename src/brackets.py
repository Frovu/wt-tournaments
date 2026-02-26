from dataclasses import dataclass
from datetime import datetime

@dataclass
class Match:
	time: datetime
	teams: list[str]
	map_winners: list[str]
	map_key: str # like rheinland_Dom

	def render(self, rn: int, mn: int, bo: int=3):
		time_str = self.time.isoformat()[:19]
		map_str = MAP_NAMES.get(self.map_key)
		if not map_str:
			raise Exception(f'Unknown map: {self.map_key}')
		
		text = f'''|R{rn}M{mn}={{{{Match
	|date={time_str}|dateexact=1|bestof={bo}
	|opponent1={{{{TeamOpponent|template={self.teams[0]}}}}}
	|opponent2={{{{TeamOpponent|template={self.teams[1]}}}}}'''
		
		for i, team in enumerate(self.map_winners, 1):
			winner = self.teams.index(team) + 1
			text += f'\n\t|map{i}={{{{Map|map={map_str}|winner={winner}}}}}'

		return text + '\n}}\n\n'
	
MAP_NAMES = {
	'tss_rheinland_Dom': 'Advance to the Rhine',
	'sinai_Dom': 'Sinai',
	'krymsk_Dom': 'Kuban',
	'vietnam_hills_Dom': 'Vietnam',
	'tss_normandy_Dom': 'Normandy'
}
	
DE_BRACKETS = {
	'64': '64U32L16DSL8DSL4DSL2DSL1D',
	'32': '32U16L8DSL4DSL2DSL1D',
	'16': '16U8L4DSL2DSL1D',
	'8': '8U4L2DSL1D',
	'4': '4U2L1D'
}

def render_double_elim(id, upper, lower):
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

	bracket = len(upper[0]) * 2
	return f'{{{{Bracket|Bracket/{DE_BRACKETS[str(bracket)]}|id=TSS{id:07}\n\n{text}}}}}\n'