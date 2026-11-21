import json,sys
K=sys.argv[1]
ACC={"A":["#f87171","#f87171","#14b8a6","#f87171","#14b8a6"],"B":["#60a5fa","#22c55e","#22c55e","#14b8a6","#14b8a6"]}[K]
KK={"A":{4:{"c2":1.5,"h":3.3,"n":4.2}},"B":{4:{"c2":1.2,"h":2.5,"n":4.2}}}[K]
scenes=[];words=[];t=0.0
NUM={"fünfzig":"50","Fünfzig":"50","hundert":"100","Hundert":"100"}
for i in range(5):
    v=json.load(open(f"reels/{K}/v{i+1}.json"));d=v["dur"]
    scenes.append({"id":f"{K}{i+1}","start":round(t,3),"dur":d,"accent":ACC[i],"k":KK.get(i,{})})
    ws=v["words"];j=0
    while j<len(ws):
        w=ws[j];txt=NUM.get(w["w"],w["w"]);s=t+w["s"];e=s+w["d"]
        if w["w"] in NUM and j+1<len(ws) and ws[j+1]["w"]=="Prozent":
            txt+="%";e=t+ws[j+1]["s"]+ws[j+1]["d"];j+=1
        words.append({"w":txt,"s":round(s,3),"e":round(e,3)});j+=1
    t+=d
json.dump({"scenes":scenes,"words":words,"total":round(t,3),"fps":30},open(f"reels/{K}/cfg.json","w"),ensure_ascii=False)
print(K,"total",round(t,2))
