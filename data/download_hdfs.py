"""Télécharge et vérifie le corpus HDFS_v1 de Loghub (Zenodo, CC-BY-4.0).

Usage : python data/download_hdfs.py   (depuis le dossier projet/)
Résultat : data/raw/HDFS_v1/ (HDFS.log + preprocessed/). Les données ne sont pas versionnées.
"""
import hashlib
import time
import urllib.request
import zipfile
from pathlib import Path

URL = "https://zenodo.org/api/records/8196385/files/HDFS_v1.zip/content"
SIZE = 186_645_559
MD5 = "76a24b4d9a6164d543fb275f89773260"

RAW = Path(__file__).resolve().parent / "raw"
ZIP = RAW / "HDFS_v1.zip"


def download():
    """Télécharge avec reprise : Zenodo coupe souvent la connexion en cours de route."""
    RAW.mkdir(parents=True, exist_ok=True)
    for attempt in range(20):
        done = ZIP.stat().st_size if ZIP.exists() else 0
        if done >= SIZE:
            return
        req = urllib.request.Request(URL, headers={"Range": f"bytes={done}-"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r, open(ZIP, "ab") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
        except OSError as e:
            print(f"Coupure ({e}), reprise à {ZIP.stat().st_size / 1e6:.0f} Mo…")
            time.sleep(2)
    raise RuntimeError("Téléchargement incomplet après 20 tentatives")


def check():
    h = hashlib.md5()
    with open(ZIP, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    if h.hexdigest() != MD5:
        raise RuntimeError(f"MD5 invalide ({h.hexdigest()}) : supprimer {ZIP} et relancer")


if __name__ == "__main__":
    download()
    check()
    with zipfile.ZipFile(ZIP) as z:
        z.extractall(RAW / "HDFS_v1")
    print(f"OK : {RAW / 'HDFS_v1'}")
