import pandas as pd

# Expected headers:
# Projections CSV:
# 'RTS ID','player','position','team','salary','rushAtts','rushYds','rushTDs',
# 'recvTgts','recvRec','recYds','recTDs','passAtts','passComp','passYds','passTDs','ints',
# 'Proj Own','projected points'
#
# Leverage CSV:
# 'Player','Pos','Team','Salary','FLEX Own','CPT Own','Total Own','FLEX Rate','CPT Rate',
# 'Total Rate','CPT Lev','Total Lev'
#
# Percentiles CSV:
# 'player','position','team','p000','p005',...,'p100'

def load_projections(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize column names
    cols = {c: c.strip() for c in df.columns}
    df.rename(columns=cols, inplace=True)
    # unify key names
    df.rename(columns={
        'player': 'Player',
        'position': 'Pos',
        'team': 'Team',
        'salary': 'Salary',
        'Proj Own': 'Total Own',
        'projected points': 'ProjPts'
    }, inplace=True)
    # Fill missing Total Own if absent
    if 'Total Own' not in df:
        df['Total Own'] = 0.0
    # Ensure dtypes
    df['Salary'] = df['Salary'].astype(int)
    if 'ProjPts' in df:
        df['ProjPts'] = df['ProjPts'].astype(float)
    return df

def load_leverage(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c: c.strip() for c in df.columns}
    df.rename(columns=cols, inplace=True)
    # Ensure dtypes
    for col in ['FLEX Own','CPT Own','Total Own','FLEX Rate','CPT Rate','Total Rate','CPT Lev','Total Lev']:
        if col in df:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    df['Salary'] = df['Salary'].astype(int)
    return df

def load_percentiles(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c: c.strip() for c in df.columns}
    df.rename(columns=cols, inplace=True)
    df.rename(columns={
        'player': 'Player',
        'position': 'Pos',
        'team': 'Team'
    }, inplace=True)
    # Ensure numeric percentiles
    for c in df.columns:
        if c.startswith('p'):
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df

def merge_inputs(proj_df: pd.DataFrame, lev_df: pd.DataFrame, pct_df: pd.DataFrame) -> pd.DataFrame:
    # Merge on Player/Team/Pos; some CSVs might have casing mismatches
    key_cols = ['Player','Pos','Team']
    for df in (proj_df, lev_df, pct_df):
        for k in key_cols:
            if k in df:
                df[k] = df[k].astype(str).str.strip()

    df = proj_df.merge(lev_df, on=key_cols+['Salary'], how='left', suffixes=('','_lev'))
    df = df.merge(pct_df, on=key_cols, how='left', suffixes=('','_pct'))

    # Fallback rates if leverage missing
    if 'CPT Rate' not in df: df['CPT Rate'] = 0.0
    if 'FLEX Rate' not in df: df['FLEX Rate'] = 0.0
    if 'Total Rate' not in df: df['Total Rate'] = df.get('Total Own', 0.0)

    # Normalize CPT/FLEX rates if they exist but don't sum meaningfully
    rates = df[['CPT Rate','FLEX Rate']].fillna(0.0)
    if (rates.sum().sum() == 0) and ('Total Own' in df):
        # derive naive split if only Total Own exists
        df['CPT Rate'] = df['Total Own'] * 0.15
        df['FLEX Rate'] = df['Total Own'] * 0.85

    # Ensure projection fallback: use p50 if ProjPts missing
    if 'ProjPts' not in df or df['ProjPts'].isna().all():
        if 'p050' in df:
            df['ProjPts'] = df['p050']
        else:
            df['ProjPts'] = 0.0

    return df
