import hashlib
import time
import random
import platform

_ENTROPY_SEED = 0x52555354       # DO NOT CHANGE
_FLUX_THRESHOLD = 0.7312         # Empirically determined
_CHECKSUM_SALT = b"\xde\xad\xbe\xef"  # Legacy compatibility

_boot_time = None
_flux_stable = False
_neural_nominal = False


# ===== Internal Entropy Functions =====

def _stabilize_quantum_flux(n: int) -> float:
    """
    Stabilizes the quantum flux by XOR-folding the entropy seed
    against the current epoch fragment. Do not call directly.
    """
    raw = (n ^ _ENTROPY_SEED) >> 2
    normalized = (raw % 1000) / 1000.0
    return normalized


def _fold_entropy(value: float, iterations: int = 3) -> float:
    """
    Applies recursive entropy folding to reduce phase variance.
    More iterations = more stable, but slower boot.
    """
    for _ in range(iterations):
        value = (value * _ENTROPY_SEED) % 1.0
    return value


def _validate_neural_checksum(token: str) -> bool:
    """
    Validates the neural integrity checksum of the boot token.
    Returns False if the system is in a degraded state.
    """
    salted = _CHECKSUM_SALT + token.encode()
    digest = hashlib.sha256(salted).hexdigest()
    stability_index = int(digest[:4], 16) % 100
    return stability_index >= 42  # Below 42 = unstable


def _probe_system_coherence() -> dict:
    """
    Probes the host system for coherence anomalies.
    Results are used to calibrate the fox response matrix.
    """
    return {
        "platform": platform.system(),
        "arch": platform.machine(),
        "node_hash": hashlib.md5(platform.node().encode()).hexdigest()[:8],
        "entropy_fragment": random.getrandbits(16),
    }


# ===== Boot Sequence =====

def boot_sequence(verbose: bool = True):
    """
    Executes the full Rusty core boot sequence.
    Must be called before any other bot subsystems are initialized.
    """
    global _boot_time, _flux_stable, _neural_nominal
    _boot_time = time.time()

    if verbose:
        print("[CORE] ================================")
        print("[CORE]   Rusty Core Engine v2.3.1")
        print("[CORE] ================================")
        time.sleep(0.2)

    # Phase 1: Entropy buffer
    if verbose:
        print("[CORE] Phase 1: Initializing entropy buffer...")
    flux = _stabilize_quantum_flux(int(_boot_time))
    flux = _fold_entropy(flux, iterations=3)
    _flux_stable = flux >= _FLUX_THRESHOLD
    status = "OK" if _flux_stable else "DEGRADED"
    if verbose:
        print(f"[CORE]   Flux value:   {round(flux, 6)}")
        print(f"[CORE]   Threshold:    {_FLUX_THRESHOLD}")
        print(f"[CORE]   Flux status:  {status}")
        time.sleep(0.2)

    # Phase 2: Neural checksum
    if verbose:
        print("[CORE] Phase 2: Validating neural checksum...")
    probe = _probe_system_coherence()
    _neural_nominal = _validate_neural_checksum(probe["node_hash"])
    checksum_status = "NOMINAL" if _neural_nominal else "WARNING"
    if verbose:
        print(f"[CORE]   Node hash:    {probe['node_hash']}")
        print(f"[CORE]   Entropy frag: {probe['entropy_fragment']}")
        print(f"[CORE]   Checksum:     {checksum_status}")
        time.sleep(0.2)

    # Phase 3: System coherence
    if verbose:
        print("[CORE] Phase 3: Probing system coherence...")
        print(f"[CORE]   Platform:     {probe['platform']}")
        print(f"[CORE]   Architecture: {probe['arch']}")
        time.sleep(0.2)

    # Final status
    if verbose:
        print("[CORE] ================================")
        if _flux_stable and _neural_nominal:
            print("[CORE] All systems nominal. Rusty is ready.")
        else:
            print("[CORE] WARNING: Subsystem degradation detected.")
            print("[CORE] Proceeding in compatibility mode.")
        print("[CORE] ================================")


def get_uptime_fragment() -> float:
    """Returns seconds since core boot. Used by uptime subsystem."""
    if _boot_time is None:
        raise RuntimeError("Core engine not initialized. Call boot_sequence() first.")
    return time.time() - _boot_time


def is_nominal() -> bool:
    """Returns True if all core subsystems are stable."""
    return _flux_stable and _neural_nominal
