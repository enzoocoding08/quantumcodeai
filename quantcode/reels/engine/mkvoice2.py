import subprocess,json,re,os,sys
exec(open("mkvoice.py").read().split("for k,lines")[0])   # reuse S
GAP=0.16
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
for k,lines in S.items():
    for i,t in enumerate(lines):
        sents=[x.strip() for x in re.split(r'(?<=[.?!:])\s+',t) if x.strip()]
        parts=[];words=[];off=0.0
        for j,s in enumerate(sents):
            f=f"reels/{k}/s{i+1}_{j}.mp3"
            subprocess.run(["python3","tts2.py",s,f],check=True)
            d=dur(f); ws=json.load(open(f+".json"))
            # trim trailing silence: end at last word end + .12
            end=min(d,max(w['s']+w['d'] for w in ws)+0.12)
            for w in ws: words.append({"w":w['w'],"s":round(off+w['s']-0.0,3),"d":w['d']})
            parts.append((f,end)); off+=end+GAP
        total=off-GAP+0.25
        # build wav: each part trimmed, with gaps
        inputs=[];flt=[];lab=[]
        for n,(f,end) in enumerate(parts):
            inputs+=["-i",f]
            flt.append(f"[{n}:a]atrim=0:{end:.3f},asetpts=PTS-STARTPTS,apad=pad_dur={GAP}[a{n}]")
            lab.append(f"[a{n}]")
        flt.append("".join(lab)+f"concat=n={len(parts)}:v=0:a=1[o]")
        subprocess.run(["ffmpeg","-y","-v","error",*inputs,"-filter_complex",";".join(flt),"-map","[o]","-ar","44100","-ac","1",f"reels/{k}/v{i+1}.wav"],check=True)
        json.dump({"dur":round(dur(f"reels/{k}/v{i+1}.wav"),3),"words":words},open(f"reels/{k}/v{i+1}.json","w"),ensure_ascii=False)
        print(k,i+1,round(dur(f"reels/{k}/v{i+1}.wav"),2),[(w['w'],round(w['s'],2)) for w in words][:30])
