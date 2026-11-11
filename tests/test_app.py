import asyncio
import app


def test_strategies_have_ten_modes():
    assert len(app.STRATEGIES) == 11
    assert "auto" in app.STRATEGIES


def test_prompt_generator_with_stubbed_local_model(monkeypatch):
    outputs = []
    async def fake_model():
        return "local-model"
    async def fake_complete(model, system, user, max_tokens):
        outputs.append((model, system, user, max_tokens))
        return "Prompt mejorado " + str(len(outputs))
    monkeypatch.setattr(app, "chosen_model", fake_model)
    monkeypatch.setattr(app, "complete", fake_complete)
    req = app.GenerateRequest(idea="Evaluar hipótesis de manipulación", strategy="experimentos", second_pass=True)
    result = asyncio.run(app.generate(req))
    assert result["model"] == "local-model"
    assert result["passes"] == 2
    assert len(outputs) == 2
    assert "experimentos" in outputs[0][2]
    assert result["prompt"] == "Prompt mejorado 2"
