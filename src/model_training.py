from pathlib import Path
import joblib
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_and_evaluate(data: pd.DataFrame, features: tuple, retained_scenario: int,
                       output_dir: Path, seed: int):
    train = data.loc[data["scenario_id"] != retained_scenario].copy()
    test = data.loc[data["scenario_id"] == retained_scenario].copy()

    X_train = train[list(features)].replace([float("inf")], float("nan"))
    X_test = test[list(features)].replace([float("inf")], float("nan"))
    valid_train = X_train.notna().all(axis=1)
    valid_test = X_test.notna().all(axis=1)
    X_train, y_train = X_train.loc[valid_train], train.loc[valid_train, "RUL_sim_hours"]
    X_test, y_test = X_test.loc[valid_test], test.loc[valid_test, "RUL_sim_hours"]

    baseline = DummyRegressor(strategy="median")
    model = ExtraTreesRegressor(
        n_estimators=500,
        min_samples_leaf=2,
        max_features=0.85,
        random_state=seed,
        n_jobs=-1,
    )
    baseline.fit(X_train, y_train)
    model.fit(X_train, y_train)

    predictions = {}
    predictions["baseline"] = baseline.predict(X_test)
    predictions["model"] = model.predict(X_test).clip(min=0)

    rows = []
    for name, prediction in predictions.items():
        rows.append({
            "modelo": name,
            "MAE_horas_sinteticas": float(mean_absolute_error(y_test, prediction)),
            "RMSE_horas_sinteticas": float(mean_squared_error(y_test, prediction) ** 0.5),
            "R2_sintetico": float(r2_score(y_test, prediction)),
        })

    metrics = pd.DataFrame(rows)
    test_result = test.loc[valid_test, ["turbine", "scenario_id", "sim_elapsed_hours", "RUL_sim_hours"]].copy()
    test_result["rul_predicted_hours"] = predictions["model"]
    test_result["residual_hours"] = test_result["RUL_sim_hours"] - test_result["rul_predicted_hours"]

    output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output_dir / "metricas_teste_sintetico.csv", index=False)
    test_result.to_csv(output_dir / "previsoes_teste_sintetico.csv.gz", index=False, compression="gzip")

    artifact = {"model": model, "features": list(features), "retained_scenario": retained_scenario,
               "model_type": "ExtraTreesRegressor", "seed": seed}
    joblib.dump(artifact, output_dir / "modelo_rul_bucha.joblib")
    return model, metrics, test_result
