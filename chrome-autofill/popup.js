const form = document.getElementById("profile-form");
const fillButton = document.getElementById("save-and-fill");
const openProfileWindowButton = document.getElementById("open-profile-window");
const popupActions = document.getElementById("popup-actions");
const introCopy = document.getElementById("intro-copy");
const status = document.getElementById("status");
const standalone = new URLSearchParams(window.location.search).get("standalone") === "1";
let saveQueue = Promise.resolve();

function showStatus(message, error = false) {
  status.textContent = message;
  status.classList.toggle("error", error);
}

function readProfile() {
  const data = new FormData(form);
  return {
    firstName: String(data.get("firstName") ?? "").trim(),
    lastName: String(data.get("lastName") ?? "").trim(),
    email: String(data.get("email") ?? "").trim(),
    phone: String(data.get("phone") ?? "").trim(),
    linkedin: String(data.get("linkedin") ?? "").trim(),
    github: String(data.get("github") ?? "").trim(),
    website: String(data.get("website") ?? "").trim(),
    city: String(data.get("city") ?? "").trim(),
    state: String(data.get("state") ?? "").trim(),
    location: String(data.get("location") ?? "").trim(),
    country: String(data.get("country") ?? "").trim(),
    overwrite: data.get("overwrite") === "on",
  };
}

async function saveProfile() {
  const profile = readProfile();
  saveQueue = saveQueue.then(() => chrome.storage.local.set({ profile }));
  await saveQueue;
  return profile;
}

async function restoreProfile() {
  const { profile = {} } = await chrome.storage.local.get("profile");
  for (const [key, value] of Object.entries(profile)) {
    const field = form.elements.namedItem(key);
    if (!field) continue;
    if (field instanceof HTMLInputElement && field.type === "checkbox") {
      field.checked = Boolean(value);
    } else {
      field.value = String(value ?? "");
    }
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await saveProfile();
    showStatus("资料已保存在本机 Chrome。", false);
  } catch (error) {
    showStatus(`保存失败：${error.message}`, true);
  }
});

form.addEventListener("input", () => {
  saveProfile()
    .then(() => showStatus("已自动保存。", false))
    .catch((error) => showStatus(`自动保存失败：${error.message}`, true));
});

form.addEventListener("change", () => {
  saveProfile()
    .then(() => showStatus("已自动保存。", false))
    .catch((error) => showStatus(`自动保存失败：${error.message}`, true));
});

openProfileWindowButton.addEventListener("click", async () => {
  openProfileWindowButton.disabled = true;
  try {
    await saveProfile();
    await chrome.windows.create({
      url: chrome.runtime.getURL("popup.html?standalone=1"),
      type: "popup",
      width: 480,
      height: 780,
    });
    window.close();
  } catch (error) {
    showStatus(`无法打开独立窗口：${error.message}`, true);
    openProfileWindowButton.disabled = false;
  }
});

fillButton.addEventListener("click", async () => {
  fillButton.disabled = true;
  showStatus("正在识别当前页面…", false);
  try {
    await saveProfile();
    const response = await chrome.runtime.sendMessage({ type: "fill-active-tab" });
    if (!response?.ok) throw new Error(response?.error ?? "填充失败");
    showStatus(`已填充 ${response.result?.filled ?? 0} 个字段，请检查后提交。`, false);
  } catch (error) {
    showStatus(`无法填充：${error.message}`, true);
  } finally {
    fillButton.disabled = false;
  }
});

if (standalone) {
  document.body.classList.add("standalone");
  popupActions.hidden = true;
  introCopy.textContent = "这个窗口切换标签页后不会关闭；输入后立即保存在本机 Chrome。";
  document.title = "编辑自动填充资料";
}

restoreProfile().catch((error) => showStatus(`读取资料失败：${error.message}`, true));
