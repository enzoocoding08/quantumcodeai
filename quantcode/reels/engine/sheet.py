import sys,subprocess
d=sys.argv[1];ts=sys.argv[2].split(',');out=sys.argv[3];cols=5
args=["ffmpeg","-y","-v","error"]
for t in ts: args+=["-i",f"{d}/test_{t}.png"]
f=";".join(f"[{i}:v]scale=405:720[v{i}]" for i in range(len(ts)))
lay="|".join(f"{(i%cols)*405}_{(i//cols)*720}" for i in range(len(ts)))
f+=";"+"".join(f"[v{i}]" for i in range(len(ts)))+f"xstack=inputs={len(ts)}:layout={lay}[o]"
subprocess.run(args+["-filter_complex",f,"-map","[o]",out],check=True)
