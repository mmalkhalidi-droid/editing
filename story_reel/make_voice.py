#!/usr/bin/env python3
"""Generate the voiceover lines (audio/lines.tsv) with ElevenLabs and print word timings."""
import json, os, subprocess, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
VOICE = "w0uhBAmNIG5kUDeaFEsA"  # Maryam Essa – Kuwaiti, female
SETTINGS = {"stability": 0.28, "similarity_boost": 0.8, "style": 0.7, "use_speaker_boost": True}
API = "https://api.elevenlabs.io/v1"
for line in open(os.path.join(D, "lines.tsv"), encoding="utf-8"):
    if not line.strip():
        continue
    i, txt = line.rstrip("\n").split("\t")
    raw, wav = os.path.join(D, f"raw{i}.mp3"), os.path.join(D, f"v{i}.wav")
    body = json.dumps({"text": txt, "model_id": "eleven_multilingual_v2", "voice_settings": SETTINGS})
    subprocess.run(["curl", "-sS", "-f", "-o", raw, "-X", "POST",
                    f"{API}/text-to-speech/{VOICE}?output_format=mp3_44100_128",
                    "-H", "xi-api-key: dummy", "-H", "Content-Type: application/json", "-d", body],
                   check=True, stdin=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:"
                    "stop_duration=0.3:stop_threshold=-45dB:stop_silence=0.25", "-ar", "44100", wav],
                   check=True, stdin=subprocess.DEVNULL)
    os.remove(raw)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav],
                         capture_output=True, text=True).stdout.strip()
    r = subprocess.run(["curl", "-sS", "-X", "POST", f"{API}/speech-to-text", "-H", "xi-api-key: dummy",
                        "-F", "model_id=scribe_v1", "-F", "language_code=ara", "-F", f"file=@{wav}"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    words = [w for w in json.loads(r.stdout).get("words", []) if w["type"] == "word"]
    print(f"== {i} {float(dur):.2f}s  " + " ".join(f"{w['text']}@{w['start']:.2f}" for w in words))
