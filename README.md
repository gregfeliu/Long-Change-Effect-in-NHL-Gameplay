# The Long Change Effect in NHL Gameplay

## Description
The goal of this project is _to make the case for having two, or even three, long changes in the NHL_. To convince the reader that this change should happen, **I review stats for 8 season of NHL gameplay and calculate the average stats per game under the two long changes and three long changes scenarios**. To "create" the two scenarios, I add the average value for a stat in the first and second periods in different combinations: for the two long changes, 2 second periods and 1 first period, and for the three long changes, three long changes. 

## Data 
The data originally came from the NHL stats API, but was collected in SQL tables [here](https://www.kaggle.com/martinellis/nhl-game-data). I stored this data in the Google Cloud Platform and used SQL queries to collect data. The SQL queries were run in Python using the mysql.connector package. I transformed and visualized this data. I also visualized the data in Tableau, creating a [story](https://public.tableau.com/profile/greg.feliu#!/vizhome/NHL_proposal_story/ExtendingtheLongChangeNHLProposal) to display my findings. 

## Findings
I find that goals, shots, the length of player shifts, and penalties will increase by a modest amount under both scenarios, more so in the three long changes scenario. 

![Bar chart showing differences in average game stats](./images/Change_in_Game_Stats_Plot.png)

These stats are all part of what is makes up "exciting hockey". The stats mean that there will be more lead changes and odd-man situations in games. 

I also find that less important categories, e.g.: takeaways, giveaways, etc., do not significantly differ under any of the proposals. 

## Presentations of Data 
The project is described in further detail in a [blog post](https://gregfeliu.medium.com/is-it-time-to-increase-the-use-of-the-long-change-in-hockey-a-proposal-for-the-nhl-132a7a3dd894). Additionally, the data is presented in a [Tableau story](https://public.tableau.com/profile/greg.feliu#!/vizhome/NHL_proposal_story/ExtendingtheLongChangeNHLProposal).

## Technologies used
- Google Cloud Platform
- Jupyter Notebook
- Tableau
- Python 
    - mysql.connector (for SQL)
    - Seaborn
    - pickle 
    - Pandas



