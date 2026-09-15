"""Stable entry point for the salary dashboard on Streamlit Community Cloud."""
from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).resolve().parent / "Rachelle Streamlit _salarycase_by_position_level.py"),
    run_name="__main__",
)
