import json
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd


def replay_scenario(data: pd.DataFrame, model, features: tuple, turbine: str,
                   scenario_id: int, threshold: float, output_dir: Path,
                   llm_on_risk_transition: bool = False):
    replay = data.loc[(data["turbine"] == turbine) &
                      (data["scenario_id"] == scenario_id)].sort_values("sim_elapsed_hours").copy()
    if replay.empty:
        raise ValueError(f"Não há dados para {turbine}, cenário {scenario_id}")

    X = replay[list(features)].replace([float("inf")], float("nan"))
    if X.isna().any().any():
        raise ValueError("Replay contém atributos ausentes ou infinitos")

    replay["rul_predicted_hours"] = model.predict(X).clip(min=0)
    replay["RUL_sim_reference_hours"] = replay["RUL_sim_hours"]
    replay["risk_flag"] = replay["rul_predicted_hours"] <= threshold
    replay["risk_transition"] = replay["risk_flag"] & ~replay["risk_flag"].shift(fill_value=False)

    records = []
    for index, row in replay.iterrows():
        event = {
            "event_id": f"{turbine}-scenario{scenario_id}-{index}",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "turbine": turbine,
            "scenario_id": scenario_id,
            "sim_elapsed_hours": float(row["sim_elapsed_hours"]),
            "rul_predicted_hours": float(row["rul_predicted_hours"]),
            "risk_threshold_hours": threshold,
            "risk_flag": bool(row["risk_flag"]),
            "risk_transition": bool(row["risk_transition"]),
            "synthetic_data": True,
        }
        if llm_on_risk_transition and bool(row["risk_transition"]):
            try:
                from src.gemini_integration import gemini_conclusion
                event["llm_conclusion"] = gemini_conclusion(event)
            except Exception as exc:
                event["llm_error"] = str(exc)[:400]
        records.append(event)

    output_dir.mkdir(parents=True, exist_ok=True)
    replay_path = output_dir / "replay_rul_local.csv.gz"
    replay[["turbine", "scenario_id", "sim_elapsed_hours", "rul_predicted_hours",
            "RUL_sim_reference_hours", "risk_flag", "risk_transition"]].to_csv(
                replay_path, index=False, compression="gzip")

    jsonl_path = output_dir / "eventos_supervisor_replay.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as stream:
        for event in records:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")

    return replay[["turbine", "scenario_id", "sim_elapsed_hours", "rul_predicted_hours",
                   "RUL_sim_reference_hours", "risk_flag", "risk_transition"]]
