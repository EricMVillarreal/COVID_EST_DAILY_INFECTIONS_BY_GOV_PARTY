# Codependcies (actually just dependencies but that makes me feel like the deadweight here)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# This provides the daily information we need
hosp_df = pd.read_csv('Reference_hospitalization_all_locs.csv')
hosp_df = pd.DataFrame(hosp_df)

# Summary statistics that might be useful for people like my ex-gf who think everything I do is inadequate
summary_df = pd.read_csv('Summary_stats_all_locs.csv')
summary_df = pd.DataFrame(summary_df)

# List of states and vassal colonies
state_names = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut",
               "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho",
               "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine",
               "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota",
               "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma",
               "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
               "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia",
               "Wyoming"]

# Liegelord affiliation dictionary
gov_party_dictionary = {"Alaska": 'R', "Alabama": 'R', "Arkansas": 'R', "American Samoa": 'D', "Arizona": 'R',
                        "California": 'D', "Colorado": 'D', "Connecticut": 'D', "District of Columbia": 'D',
                        "Delaware": 'D', "Florida": 'R', "Georgia": 'R', "Guam": 'D', "Hawaii": 'D', "Iowa": 'R',
                        "Idaho": 'R', "Illinois": 'D', "Indiana": 'R', "Kansas": 'D', "Kentucky": 'D', "Louisiana": 'D',
                        "Massachusetts": 'R', "Maryland": 'R', "Maine": 'D', "Michigan": 'D', "Minnesota": 'D',
                        "Missouri": 'R', "Mississippi": 'R', "Montana": 'D', "North Carolina": 'D', "North Dakota": 'R',
                        "Nebraska": 'R', "New Hampshire": 'R', "New Jersey": 'D', "New Mexico": 'D', "Nevada": 'D',
                        "New York": 'D', "Ohio": 'R', "Oklahoma": 'R', "Oregon": 'D', "Pennsylvania": 'D',
                        "Puerto Rico": 'NP/R', "Rhode Island": 'D', "South Carolina": 'R', "South Dakota": 'R',
                        "Tennessee": 'R', "Texas": 'R', "Utah": 'R', "Virginia": 'D', "United States Virgin Islands": 'D',
                        "Vermont": 'R', "Washington": 'D', "Wisconsin": 'D', "West Virginia": 'R', "Wyoming": 'R'}

# Filter out foreign enemies (jk, I love y'all. plz keep the petrodollar and buy our bonds)
hosp_df = hosp_df[hosp_df['location_name'].isin(state_names)]
summary_df = summary_df[summary_df['location_name'].isin(state_names)]

# Create df of population data
pop_df = pd.read_excel('State Populations.xlsx')
pop_df = pd.DataFrame(pop_df)

# Drop locations we don't location data for
hosp_df = hosp_df[hosp_df['location_name'].isin(pop_df['NAME'])]
summary_df = summary_df[summary_df['location_name'].isin(pop_df['NAME'])]

# Create 2019 population columns
pop_df = pop_df.set_index('NAME', drop=True)
hosp_df['Population'] = [int(pop_df.loc[x]) for x in hosp_df['location_name']]
summary_df['Population'] = [int(pop_df.loc[x]) for x in summary_df['location_name']]

# Create a column of party affliations using above dictionary that gave me carpal tunnel
hosp_df['Party'] = [gov_party_dictionary[x] for x in hosp_df['location_name']]
summary_df['Party'] = [gov_party_dictionary[x] for x in summary_df['location_name']]

# Create our df that gives us estimated infections by date and party affliation
grouped_hosp_df = hosp_df.groupby(['date', 'Party'])[['est_infections_upper', 'est_infections_lower',
                                                      'est_infections_mean', 'Population']].sum()

# Convert from nominal cases to cases per 100,000
for col in ['est_infections_upper', 'est_infections_lower', 'est_infections_mean']:
    grouped_hosp_df[col] = (grouped_hosp_df[col]/grouped_hosp_df['Population']) * 100000

# Fuck slices, all my friends hate slices
republican_data = grouped_hosp_df.loc[(slice(None), 'R'), :]
democrat_data = grouped_hosp_df.loc[(slice(None), 'D'), :]
weirdos_data = grouped_hosp_df.loc[(slice(None), 'NP/R'), :]

# Drop party affliation level from each so we get pretty series' (what the fuck is the plural of series? serii??)
republican_data.index = republican_data.index.droplevel(1)
democrat_data.index = democrat_data.index.droplevel(1)
weirdos_data.index = weirdos_data.index.droplevel(1)

# give the date list a better name so we can read our plotting functions better below
date_list = republican_data.index.tolist()
date_list = pd.to_datetime(date_list)

# plot my data
plt.plot(date_list, republican_data['est_infections_mean'], color='r')
plt.plot(date_list, democrat_data['est_infections_mean'], color='b')
plt.plot(date_list, weirdos_data['est_infections_mean'], color='g')
plt.legend(['Republicans', 'Democrats', 'Weirdos'])
plt.title('Estimated Infected per 100,000 by Political Affliation of State Governors')

# where the top of the dashed line should be
y_max = max(max(republican_data['est_infections_upper']), max(democrat_data['est_infections_upper']),
            max(weirdos_data['est_infections_upper']))

# Create a dashed line showing that the chart is an extrapolation past today.
plt.vlines(x=datetime.datetime.today(), ymin=0, ymax=y_max, color='grey', linestyles='dashed')
plt.text(datetime.datetime.today() + datetime.timedelta(days=4), y_max/2, 'Forecast past dashed line', rotation=90)

# Plot upper and lower bounds as fill
plt.fill_between(date_list, republican_data['est_infections_upper'], republican_data['est_infections_lower'],
                 color='r', alpha=.05)
plt.fill_between(date_list, democrat_data['est_infections_upper'], democrat_data['est_infections_lower'],
                 color='b', alpha=.05)
plt.fill_between(date_list, weirdos_data['est_infections_upper'], weirdos_data['est_infections_lower'],
                 color='g', alpha=.05)

plt.show()
