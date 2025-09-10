
# Example runner for Colab using direct GitHub RAW links.
import pandas as pd
from .config import SimConfig
from .data_io import load_projections, load_leverage, load_percentiles, merge_inputs
from .lineup import validate_player_pool
from .generator import CandidateGenerator
from .correlation import build_correlation
from .opponent import OpponentField
from .ev import EVSimulator
from .portfolio import PortfolioOptimizer

def run(proj_csv, lev_csv, pct_csv):
    cfg = SimConfig()
    proj = load_projections(proj_csv)    # accepts local path or https raw link
    lev  = load_leverage(lev_csv)
    pct  = load_percentiles(pct_csv)
    players = merge_inputs(proj, lev, pct)
    players = validate_player_pool(players)

    gen = CandidateGenerator(players, cfg)
    cands = gen.generate()

    C = build_correlation(players, cfg)
    opp = OpponentField(players, cfg)
    bank = opp.bank_field_lineups()
    field = opp.sample_field_entries(bank, n_entries=cfg.field_size - cfg.our_entries)

    sim = EVSimulator(players, C, cfg)
    ev = sim.expected_value(cands, field)

    port = PortfolioOptimizer(cfg)
    chosen = port.select(cands, ev)

    return chosen, ev.sort_values(ascending=False).head(20)

if __name__ == "__main__":
    # Paste your RAW GitHub URLs here (must start with https://raw.githubusercontent.com/...)
    projections_url  = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/projections.csv"
    leverage_url     = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/leverage.csv"
    percentiles_url  = "https://raw.githubusercontent.com/<user>/<repo>/<branch>/percentiles.csv"

    chosen, top = run(projections_url, leverage_url, percentiles_url)
    print(chosen)
    print(top)
