import numpy as np
import pandas as pd

def _pos_group(pos: str) -> str:
    pos = pos.upper()
    if pos in ['QB','RB','WR','TE','K','DST']:
        return pos
    return 'OTH'

def build_correlation(players_df: pd.DataFrame, cfg) -> np.ndarray:
    n = len(players_df)
    C = np.eye(n)
    # Precompute quick lookups
    team = players_df['Team'].to_numpy()
    pos  = players_df['Pos'].to_numpy()
    name = players_df['Player'].to_numpy()

    # Identify QBs by team (for receiver boost)
    qb_idx_by_team = {}
    for i,(t,p) in enumerate(zip(team,pos)):
        if p=='QB': qb_idx_by_team.setdefault(t, []).append(i)

    # Correlation heuristic
    for i in range(n):
        for j in range(i+1, n):
            corr = cfg.cross_team_baseline
            same_team = team[i]==team[j]
            if same_team:
                corr = cfg.base_same_team
                # boost QB with pass catchers
                if (pos[i]=='QB' and pos[j] in ('WR','TE','RB')) or (pos[j]=='QB' and pos[i] in ('WR','TE','RB')):
                    corr += cfg.qb_receiver_boost
                # mild positive kicker with offense
                if (pos[i]=='K' and pos[j] in ('QB','WR','TE','RB')) or (pos[j]=='K' and pos[i] in ('QB','WR','TE','RB')):
                    corr += cfg.k_vs_offense
                # DSTs on same team with their offense: small (driven by field position/TDs)
                if (pos[i]=='DST' and pos[j] in ('QB','WR','TE','RB','K')) or (pos[j]=='DST' and pos[i] in ('QB','WR','TE','RB','K')):
                    corr += 0.05
            else:
                # cross-team relations
                if (pos[i]=='DST' and pos[j] in ('QB','WR','TE','RB')) or (pos[j]=='DST' and pos[i] in ('QB','WR','TE','RB')):
                    corr = cfg.dst_vs_opp_offense
                if (pos[i]=='DST' and pos[j]=='DST'):
                    corr = cfg.dsts_mutual
                # very slight negative kicker vs opposing DST
                if (pos[i]=='K' and pos[j]=='DST') or (pos[j]=='K' and pos[i]=='DST'):
                    corr = min(corr, -0.05)

            C[i,j] = C[j,i] = np.clip(corr, -0.95, 0.95)

    # Ensure positive semidefinite by adding small ridge to diagonal if needed
    # (nearest PSD via eigenvalue clipping)
    eigvals, eigvecs = np.linalg.eigh(C)
    min_e = eigvals.min()
    if min_e < 1e-6:
        eigvals = np.maximum(eigvals, 1e-6)
        C = (eigvecs * eigvals) @ eigvecs.T
        # normalize diagonal back to 1
        d = np.sqrt(np.diag(C))
        C = C / (d[:,None]*d[None,:] + 1e-12)
    return C
