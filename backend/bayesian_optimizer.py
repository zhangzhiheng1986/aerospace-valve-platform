"""
Bayesian Optimization + Multi-Objective Pareto Frontier
=======================================================
Advanced optimization engine for aerospace valve design.
Supports Gaussian Process surrogate models and NSGA-II-style
multi-objective optimization with Pareto front computation.

Dependencies: numpy only (no scipy/sklearn required)
"""

import math
import time
import random
import hashlib
from dataclasses import dataclass, field

# Optional numpy acceleration
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ============================================================
# Utility Functions
# ============================================================

def _safe_div(a, b, default=0.0):
    return a / b if b != 0 else default


def _clip(val, lo, hi):
    return max(lo, min(hi, val))


def _matrix_mult(A, B):
    """Pure-Python matrix multiply A(m x n) * B(n x p) -> (m x p)."""
    if HAS_NUMPY and isinstance(A, np.ndarray) and isinstance(B, np.ndarray):
        return A @ B
    m, n = len(A), len(A[0])
    p = len(B[0])
    result = [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(p)] for i in range(m)]
    return result


def _cholesky(A):
    """Pure-Python Cholesky decomposition. A must be symmetric positive definite."""
    if HAS_NUMPY and isinstance(A, np.ndarray):
        try:
            L = np.linalg.cholesky(A)
            return L.tolist()
        except Exception:
            pass
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                val = A[i][i] - s
                if val <= 0:
                    val = 1e-10  # jitter for numerical stability
                L[i][j] = math.sqrt(val)
            else:
                L[i][j] = (A[i][j] - s) / L[j][j]
    return L


def _solve_triangular(L, b, lower=True):
    """Solve Lx = b or L^Tx = b where L is triangular."""
    n = len(L)
    x = [0.0] * n
    if lower:
        for i in range(n):
            s = sum(L[i][j] * x[j] for j in range(i))
            x[i] = (b[i] - s) / L[i][i]
    else:
        for i in range(n - 1, -1, -1):
            s = sum(L[j][i] * x[j] for j in range(i + 1, n))
            x[i] = (b[i] - s) / L[i][i]
    return x


def _lin_solve(K, y):
    """Solve K x = y via Cholesky: K = L L^T -> L (L^T x) = y."""
    L = _cholesky(K)
    z = _solve_triangular(L, y, lower=True)
    x = _solve_triangular(L, z, lower=False)
    return x


# ============================================================
# Gaussian Process Kernel
# ============================================================

def rbf_kernel(X1, X2, length_scale=1.0, signal_variance=1.0):
    """Radial Basis Function (squared exponential) kernel."""
    if HAS_NUMPY:
        X1a = np.asarray(X1, dtype=float)
        X2a = np.asarray(X2, dtype=float)
        sqdist = np.sum(X1a**2, 1).reshape(-1, 1) + np.sum(X2a**2, 1) - 2 * np.dot(X1a, X2a.T)
        K = signal_variance * np.exp(-0.5 * sqdist / length_scale**2)
        return K.tolist()
    n1, n2 = len(X1), len(X2)
    K = [[0.0] * n2 for _ in range(n1)]
    for i in range(n1):
        for j in range(n2):
            sq = sum((X1[i][k] - X2[j][k])**2 for k in range(len(X1[i])))
            K[i][j] = signal_variance * math.exp(-0.5 * sq / length_scale**2)
    return K


# ============================================================
# Bayesian Optimizer
# ============================================================

@dataclass
class OptPoint:
    x: list
    y: float
    iteration: int = 0


class BayesianOptimizer:
    """Bayesian optimization using Gaussian Process surrogate model."""

    def __init__(self, objective_fn, bounds, constraints=None,
                 length_scale=1.0, noise=1e-6):
        self.objective_fn = objective_fn
        self.bounds = bounds  # [(lo, hi), ...]
        self.constraints = constraints or []  # list of constraint_fn(x) >= 0
        self.length_scale = length_scale
        self.noise = noise
        self.dim = len(bounds)
        self.history = []  # list of OptPoint

    def optimize(self, n_iter=50, n_init=10, acq="EI", random_state=None):
        """Run Bayesian optimization for n_iter steps."""
        if random_state is not None:
            random.seed(random_state)

        self.history = []

        # Initial random sampling
        for i in range(n_init):
            x = self._random_point()
            y = self._evaluate(x)
            self.history.append(OptPoint(x, y, i))

        best = min(self.history, key=lambda p: p.y)

        for i in range(n_iter):
            # Fit GP
            X = [p.x for p in self.history]
            y = [p.y for p in self.history]
            y_mean = sum(y) / len(y)
            y_std = max(math.sqrt(sum((v - y_mean)**2 for v in y) / len(y)), 1e-6)
            y_norm = [(v - y_mean) / y_std for v in y]

            # Compute kernel matrix
            K = rbf_kernel(X, X, self.length_scale, 1.0)
            for ii in range(len(K)):
                K[ii][ii] += self.noise

            # Optimize acquisition
            x_next = self._maximize_acquisition(K, X, y_norm, y_mean, y_std,
                                                best.y, acq, n_candidates=1000)
            y_next = self._evaluate(x_next)
            iter_num = n_init + i
            self.history.append(OptPoint(x_next, y_next, iter_num))
            if y_next < best.y:
                best = OptPoint(x_next, y_next, iter_num)

        return self._result(best)

    def _maximize_acquisition(self, K, X, y_norm, y_mean, y_std,
                              best_y, acq_type, n_candidates=1000):
        """Find x that maximizes the acquisition function."""
        candidates = [self._random_point() for _ in range(n_candidates)]
        best_x = candidates[0]
        best_acq = -float("inf")

        for x_cand in candidates:
            # Predict mean and variance
            k_star = rbf_kernel([x_cand], X, self.length_scale, 1.0)[0]
            alpha = _lin_solve(K, y_norm)
            mu = sum(k_star[i] * alpha[i] for i in range(len(alpha))) * y_std + y_mean

            v = _lin_solve(K, k_star)
            k_self = rbf_kernel([x_cand], [x_cand], self.length_scale, 1.0)[0][0]
            var = max(k_self - sum(k_star[i] * v[i] for i in range(len(v))), 1e-10)
            sigma = math.sqrt(var) * y_std

            if math.isnan(mu) or math.isinf(mu):
                mu = y_mean
            if math.isnan(sigma) or math.isinf(sigma) or sigma < 1e-10:
                sigma = abs(y_std)

            # Compute acquisition
            improvement = best_y - mu
            if acq_type == "EI":  # Expected Improvement
                if sigma < 1e-10:
                    acq_val = max(0, improvement)
                else:
                    z = improvement / sigma
                    # Approximate CDF/PDF of standard normal
                    cdf_z = 0.5 * (1.0 + math.erf(z / math.sqrt(2)))
                    pdf_z = math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
                    acq_val = improvement * cdf_z + sigma * pdf_z
            elif acq_type == "UCB":  # Upper Confidence Bound (minimize, so negative)
                kappa = 2.0
                acq_val = -(mu - kappa * sigma)  # negate for minimization
            elif acq_type == "PI":  # Probability of Improvement
                if sigma < 1e-10:
                    acq_val = 1.0 if improvement > 0 else 0.0
                else:
                    z = improvement / sigma
                    acq_val = 0.5 * (1.0 + math.erf(z / math.sqrt(2)))
            else:
                acq_val = 0.0

            if math.isnan(acq_val) or math.isinf(acq_val):
                acq_val = -float("inf")

            if acq_val > best_acq:
                best_acq = acq_val
                best_x = x_cand

        return best_x

    def _random_point(self):
        return [_clip(random.uniform(lo, hi), lo, hi) for lo, hi in self.bounds]

    def _evaluate(self, x):
        """Evaluate objective with penalty for constraint violations."""
        y = self.objective_fn(x)
        penalty = 0.0
        for c in self.constraints:
            val = c(x)
            if val < 0:
                penalty += abs(val) * 1000.0
        return y + penalty

    def _result(self, best):
        return {
            "best_x": best.x,
            "best_y": best.y,
            "iterations": len(self.history),
            "history": [{"x": p.x, "y": p.y, "iteration": p.iteration} for p in self.history],
            "convergence": [p.y for p in self.history]
        }


# ============================================================
# Multi-Objective Pareto Frontier (NSGA-II style)
# ============================================================

class MultiObjectiveOptimizer:
    """Multi-objective optimization with non-dominated sorting and crowding distance."""

    def __init__(self, objectives, bounds, n_objectives=None, pop_size=50):
        """
        objectives: list of callables f(x) -> float
        bounds: [(lo, hi), ...]
        """
        self.objectives = objectives
        self.bounds = bounds
        self.n_objectives = n_objectives or len(objectives)
        self.pop_size = pop_size
        self.dim = len(bounds)
        self.history = []

    def optimize(self, n_gen=100, crossover_rate=0.9, mutation_rate=0.1,
                 mutation_scale=0.1, random_state=None):
        """Run NSGA-II-style multi-objective optimization."""
        if random_state is not None:
            random.seed(random_state)

        # Initialize population
        pop = [self._random_individual() for _ in range(self.pop_size)]

        for gen in range(n_gen):
            # Evaluate
            fitness = [self._evaluate(ind) for ind in pop]

            # Non-dominated sorting
            fronts = self._non_dominated_sort(fitness)

            # Crowding distance
            for front in fronts:
                self._crowding_distance(fitness, front)

            # Selection + Crossover + Mutation
            new_pop = []
            while len(new_pop) < self.pop_size:
                p1 = self._tournament_select(pop, fitness, fronts)
                p2 = self._tournament_select(pop, fitness, fronts)
                if random.random() < crossover_rate:
                    c1, c2 = self._crossover(p1, p2)
                    c1 = self._mutate(c1, mutation_rate, mutation_scale)
                    c2 = self._mutate(c2, mutation_rate, mutation_scale)
                    new_pop.extend([c1, c2])
                else:
                    new_pop.extend([p1, p2])

            pop = new_pop[:self.pop_size]

            # Record best front
            fitness = [self._evaluate(ind) for ind in pop]
            fronts = self._non_dominated_sort(fitness)
            pareto = [pop[i] for i in fronts[0]]
            self.history.append({
                "generation": gen,
                "pareto_size": len(pareto),
                "pareto_front": [{"x": pareto[j], "objectives": fitness[fronts[0][j]]}
                                 for j in range(len(pareto))]
            })

        # Final Pareto front
        fitness = [self._evaluate(ind) for ind in pop]
        fronts = self._non_dominated_sort(fitness)
        pareto_indices = fronts[0]
        pareto_front = [
            {"x": pop[i], "objectives": fitness[i]}
            for i in pareto_indices
        ]

        return {
            "pareto_front": pareto_front,
            "pareto_size": len(pareto_front),
            "generations": n_gen,
            "history": self.history
        }

    def _random_individual(self):
        return [_clip(random.uniform(lo, hi), lo, hi) for lo, hi in self.bounds]

    def _evaluate(self, x):
        return [obj(x) for obj in self.objectives]

    def _dominates(self, a, b):
        """Returns True if a dominates b (minimization)."""
        better = False
        for i in range(self.n_objectives):
            if a[i] > b[i]:
                return False
            if a[i] < b[i]:
                better = True
        return better

    def _non_dominated_sort(self, fitness):
        """Fast non-dominated sorting (Deb et al. 2002)."""
        n = len(fitness)
        S = [[] for _ in range(n)]  # individuals dominated by i
        domination_count = [0] * n
        fronts = [[]]

        for i in range(n):
            for j in range(i + 1, n):
                if self._dominates(fitness[i], fitness[j]):
                    S[i].append(j)
                    domination_count[j] += 1
                elif self._dominates(fitness[j], fitness[i]):
                    S[j].append(i)
                    domination_count[i] += 1

        for i in range(n):
            if domination_count[i] == 0:
                fronts[0].append(i)

        front_idx = 0
        while fronts[front_idx]:
            next_front = []
            for i in fronts[front_idx]:
                for j in S[i]:
                    domination_count[j] -= 1
                    if domination_count[j] == 0:
                        next_front.append(j)
            front_idx += 1
            fronts.append(next_front)

        return fronts[:-1] if fronts[-1] == [] else fronts

    def _crowding_distance(self, fitness, front_indices):
        """Compute crowding distance for diversity preservation."""
        if len(front_indices) <= 2:
            return

        n = len(front_indices)
        distances = [0.0] * n
        idx_map = {front_indices[i]: i for i in range(n)}

        for m in range(self.n_objectives):
            sorted_indices = sorted(front_indices, key=lambda i: fitness[i][m])
            f_min = fitness[sorted_indices[0]][m]
            f_max = fitness[sorted_indices[-1]][m]
            if f_max == f_min:
                continue
            distances[idx_map[sorted_indices[0]]] = float("inf")
            distances[idx_map[sorted_indices[-1]]] = float("inf")
            for i in range(1, n - 1):
                distances[idx_map[sorted_indices[i]]] += (
                    (fitness[sorted_indices[i + 1]][m] - fitness[sorted_indices[i - 1]][m])
                    / (f_max - f_min)
                )

        # Store distances on the individuals (extend fitness if needed)
        self._distances = distances

    def _tournament_select(self, pop, fitness, fronts):
        """Binary tournament selection based on rank and crowding distance."""
        i, j = random.randint(0, len(pop) - 1), random.randint(0, len(pop) - 1)

        # Find ranks
        rank_i = next((r for r, f in enumerate(fronts) if i in f), len(fronts))
        rank_j = next((r for r, f in enumerate(fronts) if j in f), len(fronts))

        if rank_i < rank_j:
            return pop[i]
        elif rank_j < rank_i:
            return pop[j]
        else:
            # Same rank: prefer higher crowding distance
            di = self._distances[i] if hasattr(self, "_distances") and i < len(self._distances) else 0
            dj = self._distances[j] if hasattr(self, "_distances") and j < len(self._distances) else 0
            return pop[i] if di > dj else pop[j]

    def _crossover(self, p1, p2):
        """Simulated Binary Crossover (SBX)."""
        eta = 20.0
        c1, c2 = p1[:], p2[:]
        for i in range(self.dim):
            if random.random() < 0.5:
                u = random.random()
                if u <= 0.5:
                    beta = (2 * u) ** (1.0 / (eta + 1))
                else:
                    beta = (1.0 / (2 * (1 - u))) ** (1.0 / (eta + 1))
                lo, hi = self.bounds[i]
                c1[i] = _clip(0.5 * ((1 + beta) * p1[i] + (1 - beta) * p2[i]), lo, hi)
                c2[i] = _clip(0.5 * ((1 - beta) * p1[i] + (1 + beta) * p2[i]), lo, hi)
        return c1, c2

    def _mutate(self, ind, rate, scale):
        """Polynomial mutation."""
        eta = 20.0
        result = ind[:]
        for i in range(self.dim):
            if random.random() < rate:
                lo, hi = self.bounds[i]
                u = random.random()
                delta = (hi - lo) * scale
                if u < 0.5:
                    delta_q = (2 * u) ** (1.0 / (eta + 1)) - 1
                else:
                    delta_q = 1 - (2 * (1 - u)) ** (1.0 / (eta + 1))
                result[i] = _clip(ind[i] + delta_q * delta, lo, hi)
        return result


# ============================================================
# ParetoFront Utility
# ============================================================

def compute_pareto_front(points, objectives):
    """Compute the Pareto front from a set of points with objective values.
    points: list of parameter vectors
    objectives: list of objective value vectors (same length as points)
    Returns: list of (point, objectives) on the Pareto front.
    """
    n = len(points)
    pareto = []
    for i in range(n):
        dominated = False
        for j in range(n):
            if i == j:
                continue
            # Check if j dominates i (j is at least as good in all, strictly better in at least one)
            j_better = all(objectives[j][k] <= objectives[i][k] for k in range(len(objectives[i])))
            j_strict = any(objectives[j][k] < objectives[i][k] for k in range(len(objectives[i])))
            if j_better and j_strict:
                dominated = True
                break
        if not dominated:
            pareto.append((points[i], objectives[i]))
    return pareto


# ============================================================
# Aerospace-Specific Objective Functions
# ============================================================

def solenoid_mass(x):
    """Solenoid valve mass objective (minimize). x = [D_coil, N_turns, D_wire(mm), V(V)]"""
    D, N, d, V = x
    volume = math.pi * (D / 2)**2 * (N * d * 0.001)  # m^3
    density = 7800  # kg/m^3 (steel)
    return volume * density * 1000  # grams


def solenoid_force(x):
    """Solenoid force objective (maximize, so negate). x = [D_coil, N_turns, D_wire(mm), V(V)]"""
    D, N, d, V = x
    mu0 = 4e-7 * math.pi
    gap = 0.5  # mm
    R = 0.0172 * (math.pi * D * N * 0.001) / (math.pi * (d / 2000)**2)
    I = V / max(R, 0.001)
    F = (mu0 * N**2 * I**2 * math.pi * (D / 2000)**2) / (8 * (gap / 1000)**2)
    return -F  # negate for minimization


def solenoid_cost(x):
    """Solenoid cost proxy (minimize)."""
    D, N, d, V = x
    material_cost = math.pi * D * N * d * 0.1  # proportional to wire length
    coil_cost = max(D - 10, 0) * 5  # larger D = harder to wind
    return material_cost + coil_cost


# ============================================================
# Optimization Templates
# ============================================================

OPTIMIZATION_TEMPLATES = {
    "solenoid": {
        "name": "Solenoid Valve Optimization",
        "description": "Optimize solenoid valve coil parameters for mass, force, and cost",
        "variables": [
            {"name": "coil_diameter_mm", "key": "D_coil", "lo": 10, "hi": 80},
            {"name": "turns", "key": "N_turns", "lo": 50, "hi": 2000},
            {"name": "wire_diameter_mm", "key": "d_wire", "lo": 0.1, "hi": 2.0},
            {"name": "voltage_V", "key": "V", "lo": 5, "hi": 48}
        ],
        "objectives": ["mass", "force", "cost"],
        "single_objective": {"function": "solenoid_mass", "minimize": True}
    },
    "spring": {
        "name": "Spring Design Optimization",
        "description": "Optimize valve spring for minimum mass with fatigue/strength constraints",
        "variables": [
            {"name": "wire_diameter_mm", "key": "d", "lo": 0.5, "hi": 10.0},
            {"name": "mean_coil_diameter_mm", "key": "D", "lo": 5, "hi": 60},
            {"name": "active_coils", "key": "Na", "lo": 3, "hi": 30}
        ],
        "objectives": ["mass", "stiffness", "stress"],
        "single_objective": {"function": "spring_mass", "minimize": True}
    },
    "seal": {
        "name": "Seal Design Optimization",
        "description": "Optimize O-ring / seal groove dimensions for leak rate and contact stress",
        "variables": [
            {"name": "oring_cs_mm", "key": "d2", "lo": 1.0, "hi": 7.0},
            {"name": "groove_depth_mm", "key": "h", "lo": 0.5, "hi": 6.0},
            {"name": "compression_percent", "key": "comp", "lo": 8, "hi": 30},
            {"name": "surface_roughness_um", "key": "Ra", "lo": 0.2, "hi": 3.2}
        ],
        "objectives": ["leak_rate", "contact_stress", "cost"],
        "single_objective": {"function": "leak_rate", "minimize": True}
    },
    "pressure_reducing": {
        "name": "Pressure Reducing Valve Optimization",
        "description": "Optimize PRV for regulation accuracy and flow capacity",
        "variables": [
            {"name": "orifice_diameter_mm", "key": "d_orifice", "lo": 2, "hi": 20},
            {"name": "spring_stiffness_N_per_mm", "key": "k", "lo": 1, "hi": 100},
            {"name": "diaphragm_area_mm2", "key": "A_diaphragm", "lo": 100, "hi": 5000},
            {"name": "poppet_travel_mm", "key": "travel", "lo": 0.1, "hi": 5.0}
        ],
        "objectives": ["regulation_error", "flow_capacity", "response_time"],
        "single_objective": {"function": "regulation_error", "minimize": True}
    }
}
