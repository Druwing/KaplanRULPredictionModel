from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ProjectConfig:
    project_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = project_dir
    output_dir: Path = project_dir / "outputs"
    live_turbine: str = "Turbine_2"
    retained_scenario: int = 3
    risk_threshold_hours: float = 720.0
    seed: int = 42

    features: tuple = (
        "p_closeAvg", "p_closeMin", "p_closeMax", "p_openAvg",
        "p_openMin", "p_openMax", "Glycerol",
        "abs_pressure_delta_dataset_units", "pressure_load_ratio_proxy",
        "activity_proxy_from_pressure_span", "normal_load_proxy_N",
        "oscillation_cycles_assumed_interval",
        "sliding_distance_assumed_m_interval", "wear_depth_sim_um",
    )
