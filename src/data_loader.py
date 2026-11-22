from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {
    "turbine", "scenario_id", "RUL_sim_hours",
    "p_closeAvg", "p_closeMin", "p_closeMax",
    "p_openAvg", "p_openMin", "p_openMax", "Glycerol",
}


def load_synthetic_csvs(data_dir: Path) -> pd.DataFrame:
    files = sorted(data_dir.glob("rul_sintetico_bucha_*.csv"))
    if not files:
        raise FileNotFoundError(
            "Nenhum CSV sintético encontrado. Gere os arquivos "
            "rul_sintetico_bucha_Turbine_*.csv na raiz do projeto."
        )

    frames = []
    for path in files:
        frame = pd.read_csv(path)
        missing = REQUIRED_COLUMNS.difference(frame.columns)
        if missing:
            raise ValueError(f"{path.name} não contém: {sorted(missing)}")
        frames.append(frame)

    data = pd.concat(frames, ignore_index=True)
    data = data.dropna(subset=["RUL_sim_hours"]).copy()
    data["scenario_id"] = data["scenario_id"].astype(int)
    return data
