import numpy as np
import pandas as pd
from itertools import combinations
from .lineup import is_valid_lineup, apply_cpt_salary

class CandidateGenerator:
    def __init__(self, df: pd.DataFrame, cfg):
        self.df = df.reset_index(drop=True)
        self.cfg = cfg
        self.rng = np.random.default_rng(cfg.rng_seed)

        # Precompute p50 and ranks
        self.df['p50'] = self.df.get('p050', self.df['ProjPts'])
        self.df.sort_values('p50', ascending=False, inplace=True)
        self.df.reset_index(drop=True, inplace=True)

    def _filtered_pool(self):
        # Limit pool sizes to keep enumeration feasible
        # Take top-K CPT candidates by p50, and top-K flex candidates overall
        cpt_candidates = self.df.head(self.cfg.cpt_top_k).copy()

        # Flex pool: take top flex_top_k overall + a few random longshots for leverage
        flex_top = self.df.head(self.cfg.flex_top_k).copy()
        longshots = self.df.iloc[self.cfg.flex_top_k:].sample(
            n=min(10, max(0, len(self.df)-self.cfg.flex_top_k)),
            random_state=self.cfg.rng_seed
        ) if len(self.df) > self.cfg.flex_top_k else self.df.iloc[0:0]
        flex_pool = pd.concat([flex_top, longshots], ignore_index=True).drop_duplicates(subset=['Player'])

        return cpt_candidates, flex_pool

    def generate(self, max_salary: int=None, leave_salary_max: int=None, n_samples: int=None):
        max_salary = max_salary or self.cfg.max_salary
        leave_salary_max = leave_salary_max if leave_salary_max is not None else self.cfg.leave_salary_max
        target_min_salary = max_salary - leave_salary_max

        cpt_candidates, flex_pool = self._filtered_pool()

        # Pre-index by player for quick lookups
        by_name = self.df.set_index('Player')

        # Build candidate flex combinations with pruning via simple greedy sampling
        names = flex_pool['Player'].tolist()
        candidates = set()

        # We'll sample combinations rather than brute-force all C( |pool|, 5 )
        trials = n_samples or self.cfg.candidate_pool_size * 5

        for _ in range(trials):
            # Randomly bias toward higher p50
            probs = flex_pool['p50'].to_numpy()
            probs = probs / probs.sum()
            picks = self.rng.choice(len(names), size=5, replace=False, p=probs)
            flex_names = [names[i] for i in picks]

            # Loop CPTs
            for _, row in cpt_candidates.iterrows():
                cpt = row['Player']
                ok, sal, teams = is_valid_lineup(flex_names, cpt, by_name.reset_index(), max_salary)
                if not ok: 
                    continue
                if sal < target_min_salary: 
                    continue
                lineup_key = (cpt,) + tuple(sorted(flex_names))
                candidates.add(lineup_key)
                if len(candidates) >= self.cfg.candidate_pool_size:
                    break
            if len(candidates) >= self.cfg.candidate_pool_size:
                break

        # Return as DataFrame
        out = []
        for key in candidates:
            cpt = key[0]; flex = key[1:]
            sal = apply_cpt_salary(int(by_name.loc[cpt,'Salary'])) + int(by_name.loc[list(flex),'Salary'].sum())
            out.append({'CPT': cpt, 'FLEX1': flex[0], 'FLEX2': flex[1], 'FLEX3': flex[2], 'FLEX4': flex[3], 'FLEX5': flex[4], 'Salary': sal})
        return pd.DataFrame(out)
