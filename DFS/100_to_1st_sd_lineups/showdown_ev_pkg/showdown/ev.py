import numpy as np
import pandas as pd
from scipy.stats import norm

from .percentiles import QuantileSampler

def _mvnorm_to_uniform(corr: np.ndarray, n_draws: int, rng) -> np.ndarray:
    # Draw correlated normals then map to uniforms via Phi
    Z = rng.multivariate_normal(mean=np.zeros(corr.shape[0]), cov=corr, size=n_draws)
    U = 0.5*(1+erf(Z / np.sqrt(2)))  # manual Phi
    return U

def erf(x):
    # vectorized error function using np.erf if available, else approximation
    try:
        from math import erf as m_erf
        vfunc = np.vectorize(m_erf)
        return vfunc(x)
    except Exception:
        # Abramowitz & Stegun approximation
        # Not perfect but fine for our use
        sign = np.sign(x)
        a1=0.254829592; a2=-0.284496736; a3=1.421413741; a4=-1.453152027; a5=1.061405429; p=0.3275911
        t = 1.0/(1.0+p*np.abs(x))
        y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*np.exp(-x*x)
        return sign*y

class EVSimulator:
    def __init__(self, players_df: pd.DataFrame, corr: np.ndarray, cfg):
        self.df = players_df.reset_index(drop=True)
        self.corr = corr
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.rng_seed+7)

        # Build per-player quantile samplers
        self.samplers = []
        for _, row in self.df.iterrows():
            pct = {c: row[c] for c in self.df.columns if c.startswith('p')}
            self.samplers.append(QuantileSampler(pct))

        # helpful map
        self.idx_by_name = {row['Player']: i for i, row in self.df.iterrows()}

    def simulate_points(self, n_sims: int):
        # Gaussian copula to get correlated uniforms, then inverse CDF per player
        U = self._correlated_uniforms(n_sims)
        # Map to fantasy points per player (vectorized)
        pts = np.zeros((n_sims, len(self.df)), dtype=float)
        for j, sampler in enumerate(self.samplers):
            pts[:, j] = sampler.sample(U[:, j])
        return pts  # shape (n_sims, n_players)

    def _correlated_uniforms(self, n_sims: int):
        # Use eigen-decomposition for speed / stability
        vals, vecs = np.linalg.eigh(self.corr)
        vals = np.clip(vals, 1e-8, None)
        A = vecs @ np.diag(np.sqrt(vals))
        Z = self.rng.standard_normal(size=(n_sims, self.corr.shape[0]))
        X = Z @ A.T
        # standard normal CDF
        U = 0.5 * (1.0 + erf(X / np.sqrt(2)))
        return U

    def lineup_scores(self, pts_mat: np.ndarray, lineup_df: pd.DataFrame) -> np.ndarray:
        # lineup_df columns: CPT, FLEX1..FLEX5
        idx = self.idx_by_name
        n = len(lineup_df)
        scores = np.zeros((pts_mat.shape[0], n), dtype=float)
        for k, row in lineup_df.iterrows():
            names = [row['CPT'], row['FLEX1'], row['FLEX2'], row['FLEX3'], row['FLEX4'], row['FLEX5']]
            idcs = [idx[nm] for nm in names]
            # CPT 1.5x
            s = 1.5*pts_mat[:, idcs[0]] + pts_mat[:, idcs[1]] + pts_mat[:, idcs[2]] + pts_mat[:, idcs[3]] + pts_mat[:, idcs[4]] + pts_mat[:, idcs[5]]
            scores[:, k] = s
        return scores

    def expected_value(self, our_lineups: pd.DataFrame, field_lineups: pd.DataFrame) -> pd.Series:
        n_sims = self.cfg.n_sims
        # Simulate points for all unique players
        pts = self.simulate_points(n_sims)

        # Scores
        our_scores = self.lineup_scores(pts, our_lineups)
        field_scores = self.lineup_scores(pts, field_lineups)

        # For each sim: find best score among field + our 10; tally prize split
        ev = np.zeros(our_lineups.shape[0], dtype=float)

        for t in range(n_sims):
            # combine scores
            all_scores = np.concatenate([our_scores[t], field_scores[t]])
            top = all_scores.max()
            # which our lineups tie top?
            ours_tie = np.where(our_scores[t] >= top - 1e-9)[0]
            # how many total tied?
            total_tie = (all_scores >= top - 1e-9).sum()

            if len(ours_tie) > 0:
                split = self.cfg.prize_first / total_tie
                ev[ours_tie] += split

        # average across sims
        return pd.Series(ev / n_sims, index=our_lineups.index, name='EV')
