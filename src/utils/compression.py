from pathlib import Path
import tarfile
import zipfile

from src.utils import logger


def _extract(archive, to, suffix, compression, force_reload, extract_func):
    if isinstance(to, str):
        to = Path(to)
    to.mkdir(parents=True, exist_ok=True)
    filename = archive.name.rstrip(suffix)
    if (to / filename).exists() and not force_reload:
        logger.debug("Skipping file extraction. Already exist")
    else:
        logger.debug("Extracting %s to %s", filename, to)
        extract_func(archive, to, compression)

    return to / filename


def untar(archive, to, force_reload=False, compression="gz"):
    suffix = ".tar.gz"

    def _untar(archive, to, compression):
        with tarfile.open(archive, "r:" + compression) as arc:
            arc.extractall(to)

    return _extract(archive, to, suffix, compression, force_reload, _untar)


def unzip(archive, to, suffix, force_reload=False, compression=zipfile.ZIP_DEFLATED):
    suffix = ".zip"

    def _unzip(archive, to, compression):
        with zipfile.ZipFile(archive, "r", compression=compression) as arc:
            arc.extractall(to)

    return _extract(archive, to, suffix, compression, force_reload, _unzip)


def tar(file, to, compression="gz"):
    to.mkdir(exist_ok=True, parents=True)
    arc_name = file.name
    archive = (to / arc_name).with_suffix("".join(file.suffixes + [".tar.gz"]))
    with tarfile.open(archive, "w:" + compression) as arc:
        arc.add(file, arcname=arc_name)


def zip(file, to, compression=zipfile.ZIP_DEFLATED):
    to.mkdir(exist_ok=True, parents=True)
    arc_name = file.name
    archive = (to / arc_name).with_suffix("".join(file.suffixes + [".tar.gz"]))
    with zipfile.ZipFile(archive, "w", compression=compression) as arc:
        arc.add(file, arcname=arc_name)
