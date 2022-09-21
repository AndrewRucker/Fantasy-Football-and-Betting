## Parlay betting model

The goal of this project is to see the correlation between props hitting in any given football game
With the end result being a framework that bets the most likely outcomes in the form of parlay combinations. Initial thoughts being a framework that bets both underdog and favorite correlation props.


------

Example: If team A's QB hits the over on passing yards, how likely is it that the WR1, WR2, WR3 are hitting the over on receiving stats such as yards, receptions, etc as well on team A?

What does that mean for team B, are their QB and WRs also hitting the over on their props as they try and catch up to team A's passing attack who are hitting the over on their props?

Other example: If team A's RB hits the over on rushing yards, does team B's RB hit the under on rushing yards also while team B's QB hit the over on pass attempts, WR1 over on receptions, etc because they are needing to catch up while Team A is running the clock (and potentially covering the spread)?

-------

As there is a lot of variance in interceptions, TDs, and even length of reception/passing completion
the model will be focusing primarily on yards, completions/attempts, receptions, over/under, favorite/underdog covering

At the high end, this would leave potential for 6-7 leg parlays?

-------

How will the dataset to track the test parlays look?
Binary flags. Did the over hit? Yes, 1. Did the under hit? Yes, 0. 
But how do you account for underdog/favorites? 
Different column for both. i.e. UND_RB_YDS and FAV_RB_YDS

In the dataset there will also be the over/under, spread, and whether the favorited team was at home (Binary flag).

Having more than 'only' binary flags will leave the dataset open to the possibility of seeing whether high spreads or over/under have an impact on the different parlay combinations that would hit.


The dataset will have the following columns, and be placed in Parlay_DATA.CSV
OVER_UNDER, SPREAD, FAV_HOME, FAV_QB_YDS, FAV_QB_COM, FAV_RB_ATT, FAV_RB_YDS, 
FAV_WR1_REC, FAV_WR1_YDS, FAV_WR2_REC, FAV_WR2_YDS, OVER_HIT, UNDER_HIT, FAV_COVER, UND_COVER, UND_QB_YDS, UND_QB_COM, UND_RB_YDS, UND_RB_ATT, UND_WR1_YDS, UND_WR1_REC,
UND_WR2_YDS, UND_WR2_REC

23 columns in total

--------

Rows will be the games these parlays occur in, and each game will be formatted as follows:
Chiefs 49 vs Buccanneers 17 in week 1 2021. Chiefs were the favorite so they will be listed first. In the row, the game will show as "KC49_TB17_W1_2021"

I am not sure at this moment how else to do that, but I am open to changing that game format.


So, an example row of data for this dataset will be as follows:

![image](https://user-images.githubusercontent.com/58530177/133520021-9b5fc69b-b49a-4f9b-9def-dd776175de6f.png)
 


**Disclaimer: this will be a continous work in progress**


