# Reel-Engine (Motion-Graphics, ohne Stockvideos)

Pipeline: edge-tts (Stimme + Wort-Timings) -> reel.html (animierte Szenen, per Playwright Frame fuer Frame gerendert) -> ffmpeg (Beat, Whoosh, Sidechain-Ducking, loudnorm) -> mp4 1080x1920.

1. `python3 mkvoice2.py` – Sprecher-Zeilen (S in mkvoice.py) pro Satz synthetisieren, Wort-Timings speichern
2. `python3 mkcfg.py A|B` – Szenen-Zeiten + Untertitel-Woerter -> reels/<K>/cfg.json
3. `node renderframes.js reels/<K>/cfg.json reels/<K>/frames` (Testframes: 4. Argument "0.9,3.0,...")
4. `python3 mkaudio.py A|B` – Audio-Mix
5. `ffmpeg -framerate 30 -i frames/f%05d.jpg -i audio.m4a -c:v libx264 -crf 20 -pix_fmt yuv420p ...`

Hinweise: edge-tts braucht hinter dem Proxy `certifi.where` auf /root/.ccr/ca-bundle.crt (siehe tts2.py). Szenen sind in reel.html (SC.A1..B5) definiert.
