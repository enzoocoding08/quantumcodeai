import sys, asyncio, certifi
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"   # proxy CA, verification stays on
import edge_tts
async def main(voice, text, out):
    await edge_tts.Communicate(text, voice, rate="+0%").save(out)
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))
