from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def generate_plots(test_result: pd.DataFrame, replay: pd.DataFrame,
                   metrics: pd.DataFrame, model, features: tuple, output_dir: Path):
    plt.style.use("seggressive" if "seggressive" in plt.style.available else "seaborn-v0_8-whitegrid")
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(test_result["RUL_sim_hours"], test_result["rul_predicted_hours"], s=8, alpha=.35)
    low = min(test_result["RUL_sim_hours"].min(), test_result["rul_predicted_hours"].min())
    high = max(test_result["RUL_sim_hours"].max(), test_result["rul_predicted_hours"].max())
    ax.plot([low, high], [low, high], "--", color="crimson", label="Previsão perfeita")
    ax.set(xlabel="RUL sintético de referência (h)", ylabel="RUL previsto (h)",
           title="Desempenho — previsto × referência")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "performance_predito_vs_real.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(test_result["residual_hours"], bins=50, edgecolor="white")
    ax.axvline(0, color="crimson", linestyle="--")
    ax.set(xlabel="Residual (referência − previsto, h)", ylabel="Frequência",
           title="Distribuição dos resíduos")
    fig.tight_layout()
    fig.savefig(output_dir / "performance_residuos.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(replay["sim_elapsed_hours"], replay["rul_predicted_hours"], label="RUL previsto")
    ax.plot(replay["sim_elapsed_hours"], replay["RUL_sim_reference_hours"],
            label="RUL sintético de referência", alpha=.75)
    ax.axhline(720.0, color="crimson", linestyle="--", label="Limite de risco: 720 h")
    ax.set(xlabel="Tempo de replay (h)", ylabel="RUL (h)", title="Replay da Turbine 2 — cenário retido")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "performance_replay.png", dpi=150)
    plt.close(fig)

    importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(10, 6))
    importances.sort_values().plot.barh(ax=ax)
    ax.set(xlabel="Importância", title="Atributos mais importantes")
    fig.tight_layout()
    fig.savefig(output_dir / "performance_feature_importance.png", dpi=150)
    plt.close(fig)

    metrics.to_csv(output_dir / "metricas_teste_sintetico.csv", index=False)
