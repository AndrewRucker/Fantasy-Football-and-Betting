from dataclasses import dataclass

@dataclass
class SimConfig:
    # Simulation controls
    n_sims: int = 5000                 # Monte Carlo slates
    field_size: int = 475              # total entries in contest
    our_entries: int = 10              # how many lineups we submit
    prize_first: float = 100.0         # total prize to split among 1st-place ties
    mode: str = "quantile"             # "quantile" or "stats" (stats placeholder)
    dup_penalty: float = 0.15          # penalize dup-prone lineups (0..1)
    max_salary: int = 50000            # DK cap
    leave_salary_max: int = 3500       # max salary left on table for our candidates
    max_overlap: int = 3               # max shared players among our 10 lineups
    enforce_unique_cpt: bool = False   # can toggle; portfolio optimizer will balance naturally
    rng_seed: int = 42                 # reproducibility

    # Candidate generation
    candidate_pool_size: int = 4000    # number of candidate lineups for us
    cpt_top_k: int = 15                # limit captain choices to top-K by p50 points
    flex_top_k: int = 35               # limit flex pool by p50 points (per team combined)

    # Correlation knobs for Gaussian copula (used in quantile mode)
    base_same_team: float = 0.20
    qb_receiver_boost: float = 0.25
    dst_vs_opp_offense: float = -0.30
    dsts_mutual: float = -0.20
    k_vs_offense: float = 0.05
    cross_team_baseline: float = 0.05

    # Opponent field modeling
    field_model: str = "A"             # "A" sampling by ownership, "B" optimizer-like
    field_portfolio_size: int = 8000   # bank of distinct field lineups to sample from
    field_noise_sd: float = 2.0        # points of noise in optimizer-like mode
