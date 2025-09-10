import numpy as np

class QuantileSampler:
    """Piecewise-linear inverse CDF built from provided percentiles p000..p100."""
    def __init__(self, percentiles: dict):
        # percentiles: key -> value mapping for columns like 'p000','p005',...,'p100'
        # Build sorted (q, x) arrays where q in [0,1]
        qs, xs = [], []
        for k, v in percentiles.items():
            if k.startswith('p') and v is not None and not np.isnan(v):
                try:
                    q = int(k[1:]) / 100.0  # e.g., 'p005' -> 5 -> 0.05
                except:
                    continue
                qs.append(q); xs.append(float(v))
        if len(qs) < 2:
            # fallback to degenerate distribution at 0
            qs = [0.0, 1.0]; xs = [0.0, 0.0]
        order = np.argsort(qs)
        self.q = np.array(qs)[order]
        self.x = np.array(xs)[order]

        # Enforce monotonicity in xs to avoid tiny inversions
        self.x = np.maximum.accumulate(self.x)

        # cache bounds
        self.x_min = self.x[0]
        self.x_max = self.x[-1]

    def sample(self, u: np.ndarray) -> np.ndarray:
        """Map uniforms u in [0,1] to samples via piecewise-linear inverse CDF."""
        u = np.clip(u, 0.0, 1.0)
        return np.interp(u, self.q, self.x)

    def mean(self) -> float:
        # approximate mean via trapezoidal integration of inverse CDF
        # E[X] = \int_0^1 Q(u) du ~ average of knots
        return float(np.trapz(self.x, self.q) / (self.q[-1]-self.q[0] if self.q[-1]>self.q[0] else 1.0))
