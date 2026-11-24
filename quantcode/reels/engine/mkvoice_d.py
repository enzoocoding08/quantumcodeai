import subprocess,json,sys
S={
"D":["Nvidia-Chef Jensen Huang ist zurück, und die Aktie springt an einem Tag um rund ein Drittel.","Rückblick: Nach seinem Rücktritt am zwölften November fiel die Aktie von rund hundertvierundsiebzig auf rund hundertsechsundzwanzig Dollar. Das sind etwa minus achtundzwanzig Prozent.","Am Montag setzte der Vorstand ihn laut Nvidia wieder als CEO ein. Die Aktie schloss bei hundertfünfundsechzig Dollar, plus einunddreißig Prozent zum Freitag.","Noch Tage davor hatte der Vorstand eine Rückkehr ausgeschlossen. Und selbst nach dem Sprung liegt die Aktie rund einunddreißig Prozent unter dem Hoch vom sechsten Oktober.","Eine Schlagzeile kann Kurse in beide Richtungen bewegen. Speicher dir das ab. Kein Anlagetipp, nur Bildung."],
"A":["Eine Aktie fällt um fünfzig Prozent. Wie viel Plus braucht sie, um wieder auf den alten Kurs zu kommen?",
"Die meisten sagen: fünfzig Prozent. Und genau das ist falsch.",
"Hundert Euro fallen auf fünfzig. Um wieder bei hundert zu landen, brauchst du fünfzig Euro Plus. Das sind hundert Prozent von fünfzig.",
"Darum wiegen Verluste rechnerisch schwerer. Je tiefer der Fall, desto größer das Plus, das du brauchst.",
"Speicher dir das ab und schick es jemandem, der nur auf die Rendite schaut. Kein Anlagetipp, nur Bildung."],
"B":["Dieser Chart sieht kompliziert aus. Ist er aber nicht. Alles, was du brauchst, ist eine einzige Kerze.",
"Der Körper zeigt, wo der Kurs gestartet ist und wo er geschlossen hat. Die dünnen Linien, die Dochte, zeigen das Hoch und das Tief.",
"Schließt der Kurs höher, als er gestartet ist, ist die Kerze meist grün. Schließt er tiefer, meist rot. Die Farben hängen von deiner Plattform ab.",
"Eine Kerze kann eine Minute zeigen, eine Stunde oder einen ganzen Tag. Du entscheidest den Zeitraum.",
"Speichern, damit du es nicht vergisst. Der Beispielchart ist erfunden. Kein Anlagetipp, nur Bildung."]}
for k,lines in S.items():
    for i,t in enumerate(lines):
        subprocess.run(["python3","tts2.py",t,f"reels/{k}/s{i+1}.mp3"],check=True)
        d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"reels/{k}/s{i+1}.mp3"]))
        ws=json.load(open(f"reels/{k}/s{i+1}.mp3.json"))
        print(k,i+1,round(d,2),[(w['w'],round(w['s'],2)) for w in ws][:40])
