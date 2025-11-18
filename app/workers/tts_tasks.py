import os

from app.workers.celery_app import celery_app
# from app.utils.tts.tts_query import run_tts

# @celery_app.task(name="generate_tts_task")
# def generate_tts_task(text: str, voice: str, log_id: int):
#     try:
#         result = run_tts(text, voice)
#         result["status"] = "success"
#         return result
#     except Exception as e:
#         return {"status": "fail", "error": str(e)}
#

@celery_app.task(name="generate_tts_task")
def generate_tts_task_worker(text: str, voice: str, log_id: int):
    from app.db.database import async_session_maker, RequestLog
    import asyncio, os
    from app.utils.tts.tts_query import run_tts

    async def run():
        async with async_session_maker() as session:
            try:
                res = run_tts(text, voice)
                log = await session.get(RequestLog, log_id)
                log.status = "success"
                log.audio_size = os.path.getsize(res["audio_path"])
                log.audio_link = res["filename"]

                await session.commit()
                await session.close()  # 🔹 вручную закрываем соединение
                return {"url": res["url"], "filename": res["filename"]}
            except Exception as e:
                log = await session.get(RequestLog, log_id)
                log.status = "fail"
                log.fail_reason = str(e)
                await session.commit()
                await session.close()
                return {"status": "fail", "error": str(e)}


    result = asyncio.run(run())  # 💡 теперь сохраняем return из run()
    return result  # 💡 Celery вернёт это в .result
