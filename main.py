from src.config import ProjectConfig
from src.data_loader import load_synthetic_csvs
from src.model_training import train_and_evaluate
from src.replay import replay_scenario
from src.visualization import generate_plots


def main():
    config = ProjectConfig()
    config.output_dir.mkdir(parents=True, exist_ok=True)

    data = load_synthetic_csvs(config.data_dir)
    print(f"CSV carregados: {len(data):,} linhas sintéticas")

    model, metrics, test_result = train_and_evaluate(
        data=data,
        features=config.features,
        retained_scenario=config.retained_scenario,
        output_dir=config.output_dir,
        seed=config.seed,
    )
    print(metrics.to_string(index=False))

    replay = replay_scenario(
        data=data,
        model=model,
        features=config.features,
        turbine=config.live_turbine,
        scenario_id=config.retained_scenario,
        threshold=config.risk_threshold_hours,
        output_dir=config.output_dir,
        llm_on_risk_transition=False,
    )

    generate_plots(test_result, replay, metrics, model, config.features, config.output_dir)
    print(f"Artefatos gerados em: {config.output_dir}")


if __name__ == "__main__":
    main()
