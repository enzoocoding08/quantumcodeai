import sys,asyncio,certifi,json
certifi.where=lambda:"/root/.ccr/ca-bundle.crt"
import edge_tts
async def main(text,out,voice="de-DE-ConradNeural",rate="+12%"):
    comm=edge_tts.Communicate(text,voice,rate=rate,boundary="WordBoundary")
    ws=[]
    with open(out,"wb") as f:
        async for ch in comm.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary": ws.append({"w":ch["text"],"s":ch["offset"]/1e7,"d":ch["duration"]/1e7})
    json.dump(ws,open(out+".json","w"),ensure_ascii=False)
asyncio.run(main(sys.argv[1],sys.argv[2]))
