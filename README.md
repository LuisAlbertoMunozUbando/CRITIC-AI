# CRITIC-AI — generador y auditor de prompts en NVIDIA DGX Spark

**Una idea breve → un prompt preciso → una segunda revisión crítica del prompt.**

Aplicación web local en español (FastAPI + HTML/JS sin framework de frontend) que utiliza **exclusivamente un LLM servido en la propia DGX Spark GB10**. No contiene SDK, claves ni llamadas a servicios de IA externos.

## Capacidades
- Introducir una instrucción de una frase y generar un prompt detallado, accionable y verificable.
- 10 enfoques: diagnóstico crítico, abogado del diablo, literatura, epistemología, revisión por pares, experimentos, novedad, defensa, contradicciones y auditoría final.
- Modo **Auto**: decide el enfoque a partir de la solicitud (puedes escoger manualmente).
- Dos pasadas opcionales: el modelo genera un prompt y después revisa sus ambigüedades, supuestos y condiciones de éxito.
- Ajustes de profundidad, idioma del prompt y contexto adicional. Copiar o descargar el resultado.
- Lista dinámica de modelos descubiertos en el servidor local.
- API para integrar en otros portales y aplicaciones de la Spark.

## Requisitos
- Python 3.10 o superior.
- Un servidor local de inferencia compatible con los endpoints HTTP `GET /v1/models` y `POST /v1/chat/completions` (por ejemplo, el vLLM que ya esté desplegado en Spark).
- **No descarga modelos ni modifica contenedores existentes**. El modelo real se descubre consultando el servidor; CRITIC-AI no declara qué modelo es «el más poderoso» sin observarlo.

## Inicio rápido (directamente en Spark)
```bash
git clone https://github.com/LuisAlbertoMunozUbando/CRITIC-AI.git
cd CRITIC-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Ajusta LLM_BASE_URL en .env si tu inferencia no escucha en localhost:8000
set -a; . ./.env; set +a
uvicorn app:app --host 0.0.0.0 --port 8030
```

Abrir `http://IP_DE_LA_SPARK:8030` desde la LAN (o `http://localhost:8030` en la propia máquina).

**Precaución:** la aplicación no implementa autenticación. No expongas el puerto 8030 directamente a Internet. Emplea acceso local, VPN o un proxy con autenticación.

## Con Docker
```bash
docker build -t critic-ai .
docker run --rm --network host --env-file .env critic-ai
```

Con `--network host`, `127.0.0.1:8000` significa el vLLM del host. Si se usa una red Docker aislada, configura `LLM_BASE_URL` con el nombre DNS real del servicio accesible desde el contenedor, por ejemplo `http://youtube2knowledge-llm-1:8000/v1`, **solo si ese contenedor publica esa API y puerto**.

## Configuración
| Variable | Valor inicial | Uso |
|---|---|---|
| `LLM_BASE_URL` | `http://127.0.0.1:8000/v1` | API del LLM en Spark |
| `LLM_MODEL` | vacío | Si está vacío, usa el primer modelo anunciado por `/models` |
| `LLM_API_KEY` | vacío | Solo si el servidor local exige token |
| `LLM_TIMEOUT` | `180` | Tiempo máximo por llamada, segundos |
| `MAX_INPUT_CHARS` | `16000` | Límite de texto del usuario |
| `ENABLE_SECOND_PASS` | `true` | Revisión iterativa activada por defecto |
| `PORT` | `8030` | Puerto del contenedor |

**Qué servicios se usan:** el núcleo llama al servidor LLM local. Los servicios `research-knowledge-api.service`, `youtube2knowledge-*`, `slideextractor-worker.service` e `innovation-vlm` se mantienen intactos. Su integración documental requiere confirmar sus rutas y contratos HTTP; no se han inventado endpoints. `research-knowledge-web.service` puede enlazar a CRITIC-AI como herramienta adicional.

## Ejemplo API
```bash
curl -s http://localhost:8030/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"idea":"Quiero evaluar el diseño experimental de mi robot","strategy":"experimentos","depth":"profundo","language":"es","second_pass":true}'
```

Otros endpoints: `GET /api/health`, `GET /api/models`, `GET /api/strategies`.

## Principio
La IA no sustituye el razonamiento humano: genera instrucciones que lo someten a prueba. La aplicación **no afirma haber contrastado bibliografía ni leído archivos** cuando no se le han suministrado. Los prompts piden siempre separar evidencia verificada de hipótesis.

## Pruebas
```bash
pip install -r requirements-dev.txt
pytest -q
```

## Licencia
MIT.
