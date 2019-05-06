import pandas

building_coords = {
'EER': (30.288374, -97.735322), 
'BUR': (30.288836, -97.738415), 
'UTC': (30.283224,-97.738817), 
'ECJ': (30.289065,-97.735392), 
'CPE': (30.290272, -97.736160), 
'RLM': (30.288933, -97.736434), 
'MEZ': (30.284443, -97.738986), 
'CBA': (30.284154, -97.737841), 
'GSB': (30.284140, -97.738380), 
'ART': (30.286265, -97.732985), 
'ETC': (30.289938, -97.735431),  
'CMA': (30.289246, -97.740727), 
'RLP': (30.284948, -97.735549), 
'JGB': (30.285900, -97.735731), 
'PHR': (30.288032, -97.738575), 
'SZB': (30.281665, -97.738753), 
'WAG': (30.285059, -97.737567), 
'PAR': (30.284915, -97.740110), 
'PAI': (30.287162, -97.738742), 
'GDC': (30.286233, -97.736536), 
'FNT': (30.287863, -97.737987), 
'WMB': (30.285434, -97.740401), 
'GOL': (30.285324, -97.741174), 
'BTL': (30.285445, -97.740412), 
'SUT': (30.284988, -97.740816), 
'DFA': (30.285950, -97.731741), 
'SEA': (30.290002, -97.737332), 
'GAR': (30.285173, -97.738551), 
'CAL': (30.284514, -97.740121), 
'GEA': (30.287791, -97.739214), 
'BAT': (30.284840, -97.738993), 
'BEN': (30.283986, -97.739040), 
'MRH': (30.287110, -97.730553)}

def get_building(s):
	return s.split(" ")[0]
	
def return_CT_EL(class_time):
	CT_EL = {} # dictionary for {class_time : {building : probability_distr}}
	data = pandas.read_csv('../data/Course_Info.csv')
	# print(csv_r)
	
	data['building'] = data['Room'].apply(get_building)
	data = data.groupby(['Begin Time'])


	for time, df in data:
		df = df.groupby('building')['building'].agg('count').to_frame('count').reset_index()
		for i in range(len(df)):
			room = df.iloc()[i]['building']
			count = df.iloc()[i]['count']
			if time not in CT_EL.keys():
				CT_EL[time] = {}
			CT_EL[time][room] = count
			
	for _,distr in CT_EL.items():
		total_classes = 0.0
		for _,value in distr.items():
			total_classes += value
		for key,value in distr.items():
			distr[key] /= total_classes

	return CT_EL[class_time]

print(return_CT_EL("9:00 AM"))