import json
import os


def gemini_conclusion(event: dict) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return "LLM não executado: configure GEMINI_API_KEY."

    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    model = genai.GenerativeModel(model_name)
    prompt = (
        "Analise somente este evento sintético de RUL de uma bucha Kaplan. "
        "Resuma o sinal e a incerteza em até 3 frases. Não afirme falha real, "
        "não prescreva intervenção automática e indique revisão humana obrigatória.\n" 
        + json.dumps(event, ensure_ascii=False)
    )
    return model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 220, "temperature": 0.2},
    ).text
