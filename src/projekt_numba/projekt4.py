import numpy as np
from numba import njit

@njit
def energy_change_numba(spins, i, j, N, J, B):
    s = spins[i, j]
    neighbors_sum = spins[(i-1)%N, (j-1)%N] + spins[(i-1)%N, j] + spins[(i-1)%N, (j+1)%N] + spins[i, (j-1)%N] + spins[i, (j+1)%N] + spins[(i+1)%N, (j-1)%N] + spins[(i+1)%N, j] + spins[(i+1)%N, (j+1)%N]
    dE = 2 * s * (J * neighbors_sum + B)
    return dE

@njit
def energy_numba(spins, N, J, B):
    E = 0.0
    for i in range(N):
        for j in range(N):
            s = spins[i, j]
            neighbors_sum = spins[(i-1)%N, (j-1)%N] + spins[(i-1)%N, j] + spins[(i-1)%N, (j+1)%N] + spins[i, (j-1)%N] + spins[i, (j+1)%N] + spins[(i+1)%N, (j-1)%N] + spins[(i+1)%N, j] + spins[(i+1)%N, (j+1)%N]
            E += -J * s * neighbors_sum - B * s
    return E / 2

@njit
def metropolis_step_numba(spins, N, J, beta, B):
    for spin in range(N * N):
        i = np.random.randint(0, N)
        j = np.random.randint(0, N)
        dE = energy_change_numba(spins, i, j, N, J, B)
        if dE < 0:
            spins[i, j] *= -1
        elif np.random.random() < np.exp(-beta * dE):
            spins[i, j] *= -1

@njit
def simulate_numba_with_states(spins, N, J, beta, B, M, save_every=10):
    energy_record = np.zeros(M)
    magnetization_record = np.zeros(M)
    spins_record = []
    
    for step in range(M):
        metropolis_step_numba(spins, N, J, beta, B)
        energy_record[step] = energy_numba(spins, N, J, B)
        magnetization_record[step] = np.sum(spins) / (N * N)
        
        if step % save_every == 0:
            spins_record.append(spins.copy())
    
    return energy_record, magnetization_record, spins_record