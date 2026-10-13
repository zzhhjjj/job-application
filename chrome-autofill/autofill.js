(async function autofillJobApplication() {
  const { matchField, normalize } = globalThis.JobAutofillMatcher;
  const { profile = {} } = await chrome.storage.local.get("profile");
  const values = {
    ...profile,
    fullName: [profile.firstName, profile.lastName].filter(Boolean).join(" "),
  };

  function labelText(element) {
    const labels = Array.from(element.labels ?? []).map((label) => label.textContent);
    const closestLabel = element.closest("label")?.textContent;
    return [
      ...labels,
      closestLabel,
      element.getAttribute("aria-label"),
      element.getAttribute("placeholder"),
      element.getAttribute("name"),
      element.id,
      element.getAttribute("data-testid"),
    ].filter(Boolean).join(" ");
  }

  function isUsable(element) {
    if (element.disabled || element.readOnly) return false;
    if (element.closest('[aria-hidden="true"]')) return false;
    if (element.getClientRects().length === 0) return false;
    if (element instanceof HTMLInputElement) {
      if (element.getAttribute("role") === "combobox") return false;
      return !["button", "checkbox", "file", "hidden", "password", "radio", "reset", "submit"].includes(element.type);
    }
    return element instanceof HTMLTextAreaElement || element instanceof HTMLSelectElement;
  }

  function setTextValue(element, value) {
    const prototype = element instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : HTMLInputElement.prototype;
    const setter = Object.getOwnPropertyDescriptor(prototype, "value")?.set;
    setter?.call(element, value);
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function setSelectValue(element, value) {
    const wanted = normalize(value).toLowerCase();
    const option = Array.from(element.options).find((candidate) => {
      const optionText = normalize(candidate.textContent).toLowerCase();
      const optionValue = normalize(candidate.value).toLowerCase();
      return optionText === wanted || optionValue === wanted;
    });
    if (!option) return false;
    element.value = option.value;
    element.dispatchEvent(new Event("input", { bubbles: true }));
    element.dispatchEvent(new Event("change", { bubbles: true }));
    return true;
  }

  function highlight(element) {
    const previousOutline = element.style.outline;
    const previousOffset = element.style.outlineOffset;
    element.style.outline = "2px solid #38a169";
    element.style.outlineOffset = "2px";
    window.setTimeout(() => {
      element.style.outline = previousOutline;
      element.style.outlineOffset = previousOffset;
    }, 2500);
  }

  function showToast(message, isError = false) {
    document.getElementById("job-autofill-toast")?.remove();
    const toast = document.createElement("div");
    toast.id = "job-autofill-toast";
    toast.textContent = message;
    Object.assign(toast.style, {
      position: "fixed",
      right: "20px",
      bottom: "20px",
      zIndex: "2147483647",
      maxWidth: "360px",
      padding: "12px 16px",
      borderRadius: "10px",
      background: isError ? "#8b2f2f" : "#17251d",
      color: "#ffffff",
      boxShadow: "0 10px 30px rgba(0,0,0,.25)",
      font: "14px/1.45 system-ui, sans-serif",
    });
    document.documentElement.appendChild(toast);
    window.setTimeout(() => toast.remove(), 4500);
  }

  const fields = Array.from(document.querySelectorAll("input, textarea, select"));
  const filledKeys = [];
  let filled = 0;

  for (const field of fields) {
    if (!isUsable(field)) continue;
    if (!profile.overwrite && normalize(field.value)) continue;

    const key = matchField({
      descriptor: labelText(field),
      autocomplete: field.getAttribute("autocomplete"),
      inputType: field instanceof HTMLInputElement ? field.type : "",
    });
    const value = key ? values[key] : "";
    if (!key || !normalize(value)) continue;

    const changed = field instanceof HTMLSelectElement
      ? setSelectValue(field, value)
      : (setTextValue(field, value), true);
    if (!changed) continue;

    highlight(field);
    filled += 1;
    filledKeys.push(key);
  }

  if (filled > 0) {
    showToast(`已填充 ${filled} 个字段，请检查后再提交。`);
  } else {
    showToast("没有找到可填字段；请确认资料已保存，或页面字段已经有内容。", true);
  }

  return { filled, filledKeys };
})();
