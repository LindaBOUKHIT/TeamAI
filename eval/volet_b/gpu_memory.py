"""Mesure facultative de la VRAM NVIDIA attribuée au processus courant."""
import os
import subprocess
import threading


class PeakVRAM:
    """Échantillonne la somme de VRAM du PID sur tous les GPU toutes les 0,2 s."""

    def __init__(self):
        """Prépare la mesure ; aucune dépendance GPU n'est obligatoire."""
        self.peak = None
        self._nvml = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def sample(self):
        """Renvoie des octets ou None si le pilote ne fournit pas la mémoire par PID."""
        try:
            if self._nvml is not None:
                nvml = self._nvml
                count = nvml.nvmlDeviceGetCount()
                if not count:
                    return None
                total = 0
                for index in range(count):
                    handle = nvml.nvmlDeviceGetHandleByIndex(index)
                    for proc in nvml.nvmlDeviceGetComputeRunningProcesses(handle):
                        if proc.pid == os.getpid():
                            used = proc.usedGpuMemory
                            if used is None or used == getattr(nvml, 'NVML_VALUE_NOT_AVAILABLE', 2**64 - 1):
                                return None
                            total += used
                return total
            result = subprocess.run(
                ['nvidia-smi', '--query-compute-apps=pid,used_gpu_memory', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2, check=True)
            total = 0
            for line in result.stdout.splitlines():
                pid, used = (part.strip() for part in line.split(',', 1))
                if int(pid) == os.getpid():
                    total += int(used) * 1024**2
            return total
        except (OSError, ValueError, subprocess.SubprocessError):
            return None
        except Exception:
            # pynvml expose ses propres exceptions selon le pilote et la plateforme.
            return None

    def _measure(self):
        """Actualise le pic uniquement avec une mesure disponible."""
        value = self.sample()
        if value is not None:
            self.peak = max(self.peak or 0, value)

    def _run(self):
        """Relève la mémoire jusqu'à la sortie du contexte."""
        while not self._stop.wait(0.2):
            self._measure()

    def __enter__(self):
        """Initialise NVML si importable puis démarre le relevé."""
        try:
            import pynvml
        except ImportError:
            pass
        else:
            try:
                pynvml.nvmlInit()
                self._nvml = pynvml
            except Exception:
                pass
        self._measure()
        self._thread.start()
        return self

    def __exit__(self, *exc):
        """Prend une dernière mesure et libère NVML sans masquer une erreur du run."""
        self._stop.set()
        self._thread.join()
        self._measure()
        if self._nvml is not None:
            try:
                self._nvml.nvmlShutdown()
            except Exception:
                pass
