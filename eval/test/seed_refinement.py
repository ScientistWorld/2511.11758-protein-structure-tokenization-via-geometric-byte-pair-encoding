"""Reuse identical final reference raw streams as a variant's starting point.

This is reproduction orchestration, not a decoder. All private artifacts stay
here; the variant can independently produce the same starting point via encode.
"""
import shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
for side in (HERE,HERE.parent/'train'):
 source=side/'runs/geobpe_reference'; dest=side/'runs/refined_glue'; dest.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(source/'outputs.json',dest/'outputs.base.json')
 shutil.copyfile(source/'outputs.resume.json',dest/'outputs.base.resume.json')
