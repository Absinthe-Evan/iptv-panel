const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const logBox = document.getElementById("log");

const modeSelect = document.getElementById("mode");
const pagesInput = document.getElementById("pages");

let pollingTimer = null;

/* 追加日志 */
function appendLog(text) {
  logBox.textContent += text + "\n";
  logBox.scrollTop = logBox.scrollHeight;
}

/* 更新按钮状态 */
function setRunning(running) {
  startBtn.disabled = running;
  stopBtn.disabled = !running;
}

/* 拉取状态 */
async function fetchStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();

    setRunning(data.running);

    logBox.textContent = "";
    data.logs.forEach(line => appendLog(line));
  } catch (e) {
    appendLog("[ERROR] 无法连接后端");
  }
}

/* 启动采集 */
startBtn.onclick = async () => {
  const mode = modeSelect.value;
  const pages = pagesInput.value;

  startBtn.disabled = true;

  await fetch(`/api/start?mode=${mode}&pages=${pages}`, {
    method: "POST"
  });

  fetchStatus();

  pollingTimer = setInterval(fetchStatus, 2000);
};

/* 停止采集 */
stopBtn.onclick = async () => {
  await fetch("/api/stop", { method: "POST" });

  clearInterval(pollingTimer);
  pollingTimer = null;

  fetchStatus();
};

/* 页面加载自动刷新一次 */
fetchStatus();
