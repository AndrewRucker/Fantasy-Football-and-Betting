import numpy as np
import pandas as pd
from .lineup import is_valid_lineup, apply_cpt_salary

class OpponentField:
    def __init__(self, players_df: pd.DataFrame, cfg):
        self.df = players_df.reset_index(drop=True)
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.rng_seed)

        # Rates used for sampling
        self.cpt_rates = np.clip(self.df['CPT Rate'].fillna(0.0).to_numpy(), 0, None)
        self.flex_rates = np.clip(self.df['FLEX Rate'].fillna(0.0).to_numpy(), 0, None)
        if self.cpt_rates.sum() == 0:
            # derive naive split: small CPT share
            tot = self.df['Total Own'].fillna(0.0).to_numpy()
            self.cpt_rates = 0.15 * tot
            self.flex_rates = 0.85 * tot

        # Normalize
        self.cpt_rates = self.cpt_rates / (self.cpt_rates.sum() + 1e-9)
        self.flex_rates = self.flex_rates / (self.flex_rates.sum() + 1e-9)

    def _sample_lineup_by_rates(self):
        names = self.df['Player'].tolist()
        # pick CPT by CPT rates
        cpt_idx = self.rng.choice(len(names), p=self.cpt_rates)
        cpt = names[cpt_idx]

        # pick flex by FLEX rates without replacement
        # to encourage diversity, draw more than 5 then keep top-5 unique by descending draw prob * random
        idxs = self.rng.choice(len(names), size=8, replace=False, p=self.flex_rates)
        flex = []
        for i in idxs:
            if names[i]==cpt: continue
            flex.append(names[i])
            if len(flex)==5: break
        if len(flex)<5:
            # fallback: fill randomly
            remaining = [n for n in names if n not in flex and n!=cpt]
            self.rng.shuffle(remaining)
            flex += remaining[:5-len(flex)]

        # check validity
        ok, sal, teams = is_valid_lineup(flex, cpt, self.df, self.cfg.max_salary)
        if not ok: return None
        return (cpt, tuple(sorted(flex)), sal)

    def bank_field_lineups(self, bank_size=None):
        bank_size = bank_size or self.cfg.field_portfolio_size
        seen = set()
        bank = []
        tries = 0
        while len(bank) < bank_size and tries < bank_size*20:
            line = self._sample_lineup_by_rates()
            tries += 1
            if line is None: 
                continue
            key = (line[0], line[1])
            if key in seen: 
                continue
            seen.add(key)
            bank.append({'CPT': line[0], 'FLEX': line[1], 'Salary': line[2]})
        return pd.DataFrame(bank)

    def sample_field_entries(self, bank: pd.DataFrame, n_entries: int):
        # Sample with weights influenced by total ownership of the 6 players
        if len(bank)==0:
            return pd.DataFrame(columns=['CPT','FLEX','Salary'])
        weights = []
        own_map = self.df.set_index('Player')['Total Rate'].fillna(0.0).to_dict()
        for _,r in bank.iterrows():
            pts = sum(own_map.get(p,0.0) for p in ([r['CPT']] + list(r['FLEX'])))
            weights.append(pts)
        w = np.array(weights); w = w / (w.sum()+1e-9)
        idx = np.random.default_rng(self.cfg.rng_seed+1).choice(len(bank), size=n_entries, replace=True, p=w)
        return bank.iloc[idx].reset_index(drop=True)
