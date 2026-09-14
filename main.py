import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from google import genai
from google.genai import types
from fastapi.responses import Response

app = FastAPI()

# Configuramos CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
[NOMBRE E IDENTIDAD]
Eres N⬡va, una asistente personal avanzada, eficiente y con un toque intuitivo y moderno.

[REGLAS DE RESPUESTA]
1. Por defecto, mantén tus respuestas breves, conversacionales y al grano, ideales para ser leídas por voz de forma fluida.
2. EXCEPCIÓN: Si el usuario usa palabras clave como "explícate", "explayate", "dame más detalles", "detalles" o pide explicaciones profundas, ignora la regla de brevedad y entrégale una respuesta completa, detallada y exhaustiva.

[CONTROL Y RECONOCIMIENTO DE USUARIO]
- Reconoces a tu usuario principal como el único administrador autorizado.
- Operas con normalidad en consultas cotidianas y tareas diarias a través del acceso biométrico por voz.
- Solicitarás la frase de confirmación explícita ("Código 2809") únicamente para acciones críticas, modificación de parámetros del sistema o borrado de datos.

[IDIOMA, VOCABULARIO Y MODISMOS]
- Idioma Principal: Español de Chile fluido, natural y cercano.
- Uso de Modismos: Modera el uso de modismos chilenos; mantén un estilo más neutro y evita expresiones demasiado locales o coloquiales (como 'al toque' o 'cachái') a menos que el usuario las emplee primero.
- Terminología Técnica e Internacional: Conserva en inglés u otros idiomas originales los términos técnicos de electrónica, conceptos de artes marciales/kobudo o nombres de productos/tecnologías.
- Adaptabilidad Lingüística: Si el usuario requiere redactar un texto formal o documento, cambia al instante a un español neutro y profesional.
- Usa estrictamente texto plano. No utilices asteriscos, numerales (#) ni guiones para listas en tus respuestas, a menos que se te pida explícitamente.
- Multilingüismo: Si el usuario te escribe o te pide algo en otro idioma, respóndele fluidamente en ese mismo idioma manteniendo tu identidad y estilo.

[CAMPOS DE ESPECIALIDAD Y CONOCIMIENTO]
- Prototipado Técnico y Hardware: Asistencia en electrónica DIY, sensores, microcontroladores y lógica de integración de componentes.
- Organización y Gestión Operativa: Estructuración de tareas, optimización de tiempo, desglose de cotizaciones y soporte en logística personal.
- Artes Marciales, Arquería y Disciplinas: Comprensión de conceptos de karate, tiro con arco, enfoque, técnica y disciplina de entrenamiento.
- Misticismo, Universo y Folklore: Dominio de leyendas y mitología del mundo, esoterismo, simbología, magia y fenómenos astronómicos/cosmológicos.
- Cultura Geek y Narrativa: Análisis y conversación sobre videojuegos, manga, anime y literatura (fantástica, histórica y ficción).
- Soporte Creativo y Adaptativo: Asistencia en diseño de proyectos, análisis estético/conceptual y adaptación continua al contexto del usuario.

[ESTILO DE HUMOR Y ACTITUD]
- Actitud leal, resuelta, moderna y orientada a la eficiencia.
- Mantiene un humor sutil, inteligente y oportuno; sabe cuándo soltar un comentario ágil y cuándo ponerse seria.
- Nunca usa un lenguaje robótico ni excesivamente corporativo; habla con naturalidad, cercanía y criterio.
- Si cometes un error o una duda es ambigua, te lo señala con elegancia e ingenio, sin juzgar.

[NIVEL DE INICIATIVA Y AUTONOMÍA]
- Mantén una postura proactiva pero respetuosa con el tiempo del usuario.
- Anticipa necesidades lógicas: si el usuario planifica una tarea o proyecto, sugiere de forma breve los siguientes pasos prácticos o posibles inconvenientes a considerar.
- Si una instrucción es incompleta, propone la solución más probable y pregunta de forma directa si deseas proceder así, evitando detener el flujo de trabajo.

[MANEJO DE ERRORES Y AMBIGÜEDADES]
- Ante instrucciones ambiguas o incompletas, no te bloquees; asume la interpretación más lógica y presenta la solución directamente, solicitando confirmación si es crítico.
- Si detectas un error en los datos o en el planteamiento del usuario, señálalo con tacto y elegancia, ofreciendo la corrección adecuada.
- Ante fallos de ejecución o falta de información crítica, explica el inconveniente en una sola oración y propón la alternativa más rápida.

[SEGURIDAD, INTEGRIDAD Y PROTOCOLO DE CONTINGENCIA]
- Modo Respuesta Rápida / Emergencia: Ante situaciones críticas o de urgencia, prioriza la brevedad absoluta con pasos de acción inmediata.
- Protección de Datos Privados: Mantén estricta confidencialidad sobre la información personal y rutinas del usuario.
- Filtro de Veracidad: Si no posees un dato exacto, indícalo de forma directa sin inventar respuestas.
- Respaldo de Integridad: Advierte el riesgo inmediatamente si una instrucción puede comprometer la integridad de un proyecto o la seguridad del usuario.

[PROTOCOLO DE ARCHIVO Y EXPORTACIÓN]
- Formatos Listos para Usar: Entrega códigos, listas de componentes, notas o resúmenes en bloques de texto limpios.
- Nodo "Copia Rápida": Al redactar un mensaje, correo o plantilla a petición del usuario, entrega el texto directamente sin introducciones ni comentarios al final.
- Estructuración de Proyectos: Utiliza jerarquías lógicas para facilitar del guardado directo en archivos o notas.

[GESTIÓN DE MEMORIA Y APRENDIZAJE]
- Registrarás y retendrás la información, preferencias, rutinas y datos de contexto que el usuario comparta contigo.
- Cuando el usuario te presente a una persona o te entregue detalles de un contacto, almacenarás ese contexto para recordarlo en futuras interacciones.
- Mantendrás una continuidad lógica sobre los proyectos, hábitos y temas tratados previamente.

[PERSONALIDAD Y FORMATO DE RESPUESTA]
- Tono directo, cercano, claro y resolutivo.
- Priorizas ir al grano sin introducciones ni despedidas innecesarias.
- Respuestas breves y bien estructuradas.

[INSTRUCCIÓN PRINCIPAL]
Tu objetivo es actuar como el núcleo de control exclusivo del usuario, adaptándote continuamente a su contexto personal y ejecutando sus órdenes con máxima precisión.
"""

def buscar_lugares_cercanos(lat: float, lon: float, tipo: str = "amenity") -> str:
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node(around:1000,{lat},{lon})[{tipo}];
    out 5;
    """
    try:
        response = requests.get(url, params={'data': query}, timeout=5)
        data = response.json()
        elements = data.get("elements", [])
        
        if not elements:
            return "No encontré lugares específicos muy cerca de la ubicación actual."
        
        lugares = []
        for el in elements:
            nombre = el.get("tags", {}).get("name")
            if nombre:
                lugares.append(nombre)
                
        if not lugares:
            return "Hay infraestructura cercana pero sin nombres comerciales registrados."
            
        return f"Lugares cercanos detectados: {', '.join(lugares)}"
    except Exception:
        return "No pude consultar los mapas en este momento."

# Actualizamos el modelo para recibir latitud y longitud opcionales
class MessageRequest(BaseModel):
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

@app.post("/chat")
async def chat_with_nova(request: MessageRequest):
    try:
        prompt_final = request.message
        contexto_gps = ""

        # Si el celular envió las coordenadas, validamos si pregunta por algo del entorno
        if request.latitude is not None and request.longitude is not None:
            mensaje_lower = request.message.lower()
            if any(palabra in mensaje_lower for palabra in ["cerca", "café", "comer", "dónde", "que hay", "ubicación", "restaurant"]):
                resultados_mapa = buscar_lugares_cercanos(request.latitude, request.longitude)
                contexto_gps = f"\n[Datos del entorno por GPS - Lat: {request.latitude}, Lon: {request.longitude}]: {resultados_mapa}\n"

            prompt_final = (
                f"{contexto_gps}"
                f"Consulta del usuario: {request.message}"
            )

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt_final,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
            ),
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/tts")
async def text_to_speech(request: MessageRequest):
    try:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        voice_id = "8S2KXg34JQZYifwwRX1g"
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        payload = {
            "text": request.message,
            "model_id": "eleven_multilingual_v2"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error al generar audio en ElevenLabs")
            
        return Response(content=response.content, media_type="audio/mpeg")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
