import json,urllib.request,sys
S={
 "whoosh":("Fast clean swoosh transition whoosh, modern social media video transition, short",0.7),
 "pop":("Cute bubbly pop sound, UI pop, speech bubble appearing, crisp and short",0.4),
 "boing":("Cartoon curious question boing, playful short wobble sound",0.8),
 "ding":("Bright positive notification ding, single bell chime, clean",0.8),
 "wrong":("Short wrong answer buzzer, game show error buzz, quiz incorrect, quick",0.5),
 "check":("Short soft correct answer tick, satisfying UI check chime, quick",0.4),
 "slide":("Soft paper card swipe slide in, light swish",0.5),
 "shake":("Phone vibrate buzz rattle, frustrated shaking, short",1.0),
 "marker":("Fast marker pen strike-through scribble on paper, quick swipe",0.6),
 "sparkle":("Magical rising sparkle shimmer, gentle twinkle swell",1.6),
 "reveal":("Logo reveal impact, deep cinematic hit with bright shimmer tail, modern brand intro",2.2),
}
for n,(p,d) in S.items():
    if len(sys.argv)>1 and n not in sys.argv[1:]: continue
    req=urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128",
      data=json.dumps({"text":p,"duration_seconds":max(0.5,d),"prompt_influence":0.6}).encode(),headers={"Content-Type":"application/json"})
    try: open(f"{n}.mp3","wb").write(urllib.request.urlopen(req).read()); print("ok",n)
    except urllib.error.HTTPError as e: print("ERR",n,e.code,e.read()[:200])
