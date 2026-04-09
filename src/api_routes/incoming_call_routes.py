from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from langdetect import detect, LangDetectException
import json
from datetime import datetime
#To enable input box in swagger
from pydantic import BaseModel

class SimulateRequest(BaseModel):
    text: str
# Creating router for handling incoming call related APIs
incoming_call_router = APIRouter()
# API to handle incoming calls
@incoming_call_router.post("/incoming-call")
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        #works for local server
        #action="http://127.0.0.1:8000/process-speech",
        #works for twilio realtime
        action="https://pecuniarily-nonextracted-bettye.ngrok-free.dev/process-speech",
        #method="post",
        method="POST",
        timeout=5,
        speechTimeout="auto"
    )
    gather.say("Hello,welcome with Doctomed.")
    response.append(gather)
    #Fallback if no language detected
    response.say("Which language do you prefer?")
    return Response(content=str(response), media_type="application/xml")
@incoming_call_router.post("/process-speech")
async def process_speech(request: Request):
    form_data = await request.form()
    #Get what user spoke(Twilio sends this)
    user_input = form_data.get("SpeechResult","").lower()
    response = VoiceResponse()

    detected_language = None
    intent = "unknown"
    system_reply = ""

    #  Language detection
    try:
        detected_language = detect(user_input)
    except LangDetectException:
        detected_language = None

    #  Language fallback
    if not detected_language:
        system_reply = "Which language do you prefer?"
        response.say(system_reply)
        return Response(content=str(response), media_type="application/xml")
    else:
        #  Emergency
        if any(word in user_input for word in ["chest pain", "accident", "bleeding"]):
            intent = "emergency"
            system_reply = "This may be a medical emergency. Please call 144 or 112 immediately."
            response.say(system_reply)

        #  Hospital
        elif "hospital" in user_input:
            intent = "hospital"
            system_reply = "The nearest hospital is Zurich General Hospital."
            response.say(system_reply)

        #  Pharmacy
        elif "pharmacy" in user_input or "medicine" in user_input:
            intent = "pharmacy"
            system_reply = "The nearest pharmacy is City Care Pharmacy."
            response.say(system_reply)

        #  Unknown
        else:
            system_reply = "I did not understand your request. Please try again."
            response.say(system_reply)

    #  LOG DATA 
    log_data = {
        "timestamp": str(datetime.now()),
        "user_input": user_input,
        "language": detected_language,
        "intent": intent,
        "response": system_reply
    }

    with open("call_logs.json", "a") as f:
        f.write(json.dumps(log_data) + "\n")

    gather = Gather(
    input="speech",
    action="https://pecuniarily-nonextracted-bettye.ngrok-free.dev/process-speech",
    method="POST",
    timeout=5,
    speechTimeout="auto"
    )

    gather.say("How else can I assist you?")

    response.append(gather)

    return Response(content=str(response), media_type="application/xml")

#To Manually Test output by giving input in swagger
@incoming_call_router.post("/simulate-call")
async def simulate_call(data: SimulateRequest):

    user_input = data.text.lower()

    response_text = ""
    intent = "unknown"
    detected_language = None

    # 🔤 Language detection
    try:
        detected_language = detect(user_input)
    except LangDetectException:
        detected_language = None

    if not detected_language:
        response_text = "Which language do you prefer?"

    else:
        if any(word in user_input for word in ["chest pain", "accident", "bleeding"]):
            intent = "emergency"
            response_text = "This may be a medical emergency. Please call 144 or 112 immediately."

        elif "hospital" in user_input:
            intent = "hospital"
            response_text = "The nearest hospital is Zurich General Hospital."

        elif "pharmacy" in user_input or "medicine" in user_input:
            intent = "pharmacy"
            response_text = "The nearest pharmacy is City Care Pharmacy."

        else:
            response_text = "I did not understand your request. Please try again."

    return {
        "user_input": user_input,
        "language": detected_language,
        "intent": intent,
        "response": response_text
    }
