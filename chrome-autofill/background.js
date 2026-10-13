async function fillTab(tabId) {
  const results = await chrome.scripting.executeScript({
    target: { tabId },
    files: ["matcher.js", "autofill.js"],
  });
  return results.at(-1)?.result ?? { filled: 0 };
}

async function fillActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) throw new Error("找不到当前标签页");
  return fillTab(tab.id);
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.type !== "fill-active-tab") return undefined;

  fillActiveTab()
    .then((result) => sendResponse({ ok: true, result }))
    .catch((error) => sendResponse({ ok: false, error: error.message }));
  return true;
});

chrome.commands.onCommand.addListener((command) => {
  if (command !== "fill-current-page") return;
  fillActiveTab().catch(() => undefined);
});
