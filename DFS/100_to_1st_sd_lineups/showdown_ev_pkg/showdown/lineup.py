from dataclasses import dataclass
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

ALLOWED_POS = {'QB','WR','RB','TE','K','DST'}

@dataclass(frozen=True)
class Lineup:
    cpt: str              # player name @ CPT
    flex: Tuple[str,...]  # 5 player names
    salary: int
    teams: Tuple[str,...] # teams present
    players: Tuple[str,...] # all 6 names (CPT duplicates prevented upstream)

def apply_cpt_salary(base_salary: int) -> int:
    # EXACT 1.5x (no rounding beyond int)
    return int(round(1.5 * base_salary))

def is_valid_lineup(names: List[str], cpt_name: str, df: pd.DataFrame, max_salary: int) -> Tuple[bool,int,Tuple[str,...]]:
    # Ensure no duplicate CPT in flex, both teams present, salary cap
    if cpt_name in names:
        return False, 0, ()
    all_names = [cpt_name] + names
    rows = df.set_index('Player').loc[all_names]
    salary = apply_cpt_salary(int(rows.loc[cpt_name,'Salary'])) + int(rows.loc[names, 'Salary'].sum())
    if salary > max_salary:
        return False, salary, ()
    teams = set(rows['Team'].tolist())
    if len(teams) < 2:
        return False, salary, ()
    return True, salary, tuple(teams)

def validate_player_pool(df: pd.DataFrame) -> pd.DataFrame:
    # Filter to allowed positions and players expected active
    df = df[df['Pos'].isin(ALLOWED_POS)].copy()
    # basic sanity
    df = df.dropna(subset=['Player','Pos','Team','Salary','ProjPts'])
    return df
