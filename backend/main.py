from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import threading
import time
import os

app = FastAPI(title="IPTV Panel")

# 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 状态控制
spider_process = None
spider_logs = []
is_running = False


def log(msg: str):
    timestamp = time.strftime("[%H:%M:%S]")
    spider_logs.append(f"{timestamp} {msg}")
    if len(spider_logs) > 500:
        spider_logs.pop(0)


@app.get("/api/status")
def status():
    return {
        "running": is_running,
        "logs": spider_logs[-100:]
    }


@app.post("/api/start")
def start_spider(mode: str = "multicast", pages: int = 1):
    global spider_process, is_running

    if is_running:
        return JSONResponse(
            {"error": "Spider already running"},
            status_code=400
        )

    is_running = True
    log(f"后台采集任务启动：类型={mode}，页数={pages}")

    def run():
        global spider_process, is_running
        try:
            spider_process = subprocess.Popen(
                [
                    "docker", "run", "--rm",
                    "-v", f"{os.getcwd()}/data:/data",
                    "ghcr.io/cqshushu/iptv-spider:latest"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in spider_process.stdout:
                log(line.strip())

        except Exception as e:
            log(f"错误：{e}")
        finally:
            is_running = False
            log("采集任务结束")

    threading.Thread(target=run, daemon=True).start()
    return {"message": "采集已启动"}


@app.post("/api/stop")
def stop_spider():
    global spider_process, is_running

    if spider_process and is_running:
        spider_process.terminate()
        is_running = False
        log("采集任务已停止")
        return {"message": "已停止"}
    return {"message": "未运行"}


# 前端静态页面（后面会放）
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
