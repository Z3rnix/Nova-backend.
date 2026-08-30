import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Modelo para recibir el JSON {"texto": "..."}
class MensajeInput(BaseModel):
    texto: str

@app.get("/")
async def raiz():
    return {"estado": "NOva backend activo y operativo"}

@app.post("/hablar")
@app.post("/hablar_con_nova")
async def hablar(datos: MensajeInput):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return {"respuesta": "Error: La clave GEMINI_API_KEY no está configurada en Render."}

        # Inicializar el cliente con la API Key
        client = genai.Client(api_key=api_key)

        # Llamada al modelo Gemini 2.5 Flash
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=datos.texto,
        )

        return {"respuesta": response.text}

    except Exception as e:
        # Captura cualquier error sin tumbar el servidor Uvicorn
        return {"respuesta": f"Error interno en N⬡va: {str(e)}"}
