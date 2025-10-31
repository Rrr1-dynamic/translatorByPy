import gradio as gr
import speech_recognition as sr
from gtts import gTTS
import os, tempfile, uuid
from deep_translator import GoogleTranslator

# Recognizer
recog = sr.Recognizer()

# Language Mapping
lang_map = {
    "Auto Detect": "auto",  
    "Hindi": "hi",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Bengali": "bn",
    "Japanese": "ja"
}

# Core Translation Function 
def run_translation(text, source_lang, target_lang):
    try:
        if not text or text.strip() == "":
            return "Error", "Please enter or speak some text.", None

        # Convert Names To Codes
        source_code = lang_map.get(source_lang, "auto")
        target_code = lang_map.get(target_lang, "en")

        # Translate
        translated = GoogleTranslator(source=source_code, target=target_code).translate(text)
        print(f"Translated: {translated}")

        # Text To Speech (unique file)
        file_path = os.path.join(tempfile.gettempdir(), f"translated_{uuid.uuid4().hex}.mp3")
        tts = gTTS(translated, lang=target_code)
        tts.save(file_path)

        return text, translated, file_path

    except Exception as e:
        return "Error", f"Translation error: {str(e)}", None


# Speech via Microphone
def translate_speech(source_lang, target_lang):
    try:
        with sr.Microphone() as source:
            recog.adjust_for_ambient_noise(source, duration=1)
            print("🎤 Speak something...")
            audio = recog.listen(source, timeout=8, phrase_time_limit=12)

        # Speech To Text
        text = recog.recognize_google(audio)
        print(f"Original (Mic): {text}")

        return run_translation(text, source_lang, target_lang)

    except sr.WaitTimeoutError:
        return "Error", "⏱ No speech detected (timeout). Try again.", None
    except sr.UnknownValueError:
        return "Error", "❌ Could not understand your speech.", None
    except sr.RequestError as e:
        return "Error", f"⚠ Speech Recognition API error: {e}", None
    except Exception as e:
        return "Error", f"Unexpected error: {str(e)}", None


# Gradio UI 
with gr.Blocks() as demo:
    gr.Markdown("## 🌍 Voice + Text Translator\nMic OR Text → Translate → Audio Output")

    with gr.Tab("🎤 Mic Input"):
        src_lang_s = gr.Dropdown(list(lang_map.keys()), value="Auto Detect", label="Select Input Language")
        tgt_lang_s = gr.Dropdown(list(lang_map.keys()), value="Hindi", label="Select Output Language")
        btn_speech = gr.Button("Start Recording & Translate")
        out_orig_s = gr.Textbox(label="🎙 Original Speech")
        out_trans_s = gr.Textbox(label="🌐 Translated Text")
        out_audio_s = gr.Audio(label="🔊 Translated Voice", type="filepath")

        btn_speech.click(translate_speech, inputs=[src_lang_s, tgt_lang_s], outputs=[out_orig_s, out_trans_s, out_audio_s])

    with gr.Tab("⌨ Text Input"):
        text_in = gr.Textbox(label="Enter text here")
        src_lang_t = gr.Dropdown(list(lang_map.keys()), value="Auto Detect", label="Select Input Language")
        tgt_lang_t = gr.Dropdown(list(lang_map.keys()), value="Hindi", label="Select Output Language")
        btn_text = gr.Button("Translate Text")
        out_orig_t = gr.Textbox(label="📝 Original Text")
        out_trans_t = gr.Textbox(label="🌐 Translated Text")
        out_audio_t = gr.Audio(label="🔊 Translated Voice", type="filepath")

        btn_text.click(run_translation, inputs=[text_in, src_lang_t, tgt_lang_t], outputs=[out_orig_t, out_trans_t, out_audio_t])

demo.launch(share=True)