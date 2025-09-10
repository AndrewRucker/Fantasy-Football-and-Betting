import numpy as np
import pandas as pd

def _overlap(a_row, b_row):
    a = set([a_row['CPT'], a_row['FLEX1'], a_row['FLEX2'], a_row['FLEX3'], a_row['FLEX4'], a_row['FLEX5']])
    b = set([b_row['CPT'], b_row['FLEX1'], b_row['FLEX2'], b_row['FLEX3'], b_row['FLEX4'], b_row['FLEX5']])
    return len(a & b)

class PortfolioOptimizer:
    def __init__(self, cfg):
        self.cfg = cfg

    def select(self, candidates: pd.DataFrame, ev: pd.Series):
        # Greedy submodular-like selection:
        # maximize EV while enforcing max overlap and mild CPT diversity, salary leave <= cfg.leave_salary_max
        df = candidates.copy()
        df = df.join(ev)
        df = df.sort_values('EV', ascending=False).reset_index(drop=True)

        chosen_idx = []
        cpts_used = set()

        for i, row in df.iterrows():
            if len(chosen_idx) >= self.cfg.our_entries:
                break
            # overlap constraint
            ok = True
            for j in chosen_idx:
                if _overlap(row, df.loc[j]) > self.cfg.max_overlap:
                    ok = False; break
            if not ok: 
                continue
            # Optional CPT uniqueness encouragement (not strict)
            if self.cfg.enforce_unique_cpt and row['CPT'] in cpts_used:
                continue

            chosen_idx.append(i)
            cpts_used.add(row['CPT'])

        return df.loc[chosen_idx].reset_index(drop=True)
