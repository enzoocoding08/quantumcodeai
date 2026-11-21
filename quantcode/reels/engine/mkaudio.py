import json,subprocess,sys
K=sys.argv[1];cfg=json.load(open(f"reels/{K}/cfg.json"));tot=cfg["total"]
ins=[]
for i in range(5): ins+=["-i",f"reels/{K}/v{i+1}.wav"]
flt=["[0:a][1:a][2:a][3:a][4:a]concat=n=5:v=0:a=1,aformat=sample_rates=44100:channel_layouts=stereo,asplit[vo][vo2]"]
n=5
def src(expr,label,dur):
    global n
    ins.extend(["-f","lavfi","-t",f"{dur:.2f}","-i",expr]);idx=n;n+=1;return idx
d=tot+1
kick=src("aevalsrc='0.9*sin(2*PI*(48+110*exp(-38*mod(t,0.6)))*mod(t,0.6))*exp(-8*mod(t,0.6))':s=44100","k",d)
hat=src("aevalsrc='(random(0)*2-1)*exp(-70*mod(t+0.3,0.6))*0.5':s=44100","h",d)
pad=[src(f"sine=f={f}:r=44100","p",d) for f in (110,164.81,220,277.18)]
flt.append(f"[{kick}:a]aformat=channel_layouts=stereo,volume=0.55[kk]")
flt.append(f"[{hat}:a]highpass=f=6500,aformat=channel_layouts=stereo,volume=0.22[hh]")
for j,p in enumerate(pad): flt.append(f"[{p}:a]aformat=channel_layouts=stereo,volume=0.05,tremolo=f={0.35+0.1*j}:d=0.6[pp{j}]")
flt.append("[kk][hh][pp0][pp1][pp2][pp3]amix=inputs=6:normalize=0,lowpass=f=9000[bed]")
flt.append("[bed][vo2]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=350[duck]")
wh=[]
for si,s in enumerate(cfg["scenes"]):
    w=src("anoisesrc=d=0.5:c=pink:r=44100",f"w{si}",0.5)
    ms=int(s["start"]*1000)+0
    flt.append(f"[{w}:a]aformat=channel_layouts=stereo,highpass=f=900,lowpass=f=7000,afade=t=in:d=0.22,afade=t=out:st=0.22:d=0.28,volume=0.30,adelay={ms}|{ms}[w{si}]");wh.append(f"[w{si}]")
flt.append("[vo]volume=1.0[v]")
flt.append("[v][duck]"+"".join(wh)+f"amix=inputs={2+len(wh)}:normalize=0,atrim=0:{tot:.2f},loudnorm=I=-15:TP=-1.5:LRA=9[out]")
subprocess.run(["ffmpeg","-y","-v","error",*ins,"-filter_complex",";".join(flt),"-map","[out]","-c:a","aac","-b:a","192k","-ar","44100",f"reels/{K}/audio.m4a"],check=True)
print("audio ok",K)
