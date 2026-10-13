# Job Application Autofill

A local Chrome extension that fills common job-application fields. It stores the profile in `chrome.storage.local`, makes no network requests, never uploads a résumé, and never submits an application.

## Install locally

1. Open `chrome://extensions` in Chrome.
2. Enable **Developer mode**.
3. Click **Load unpacked**.
4. Select this `chrome-autofill` directory.
5. Pin **Job Application Autofill** from the extensions menu.

## Use

1. Open the extension. Every change is saved automatically.
2. Use **在独立窗口编辑** when you need to switch tabs to find LinkedIn, GitHub, or other profile details. The independent window stays open.
3. On an application page, click **保存并填充当前页**.
4. Or press `Alt+Shift+F` after saving the profile.
5. Review every highlighted field before submitting.

After changing the extension files, open `chrome://extensions` and click the extension's reload button once.

The extension fills First name, Last name, Full legal name, Email, Phone, LinkedIn, GitHub, Personal website, Location, City, State, and native Country selects. Existing values are preserved unless **覆盖已有内容** is enabled.

## Safety boundaries

- No automatic submission.
- No résumé upload.
- No automatic answers for work authorization, sponsorship, compensation, demographic, disability, veteran, or legal attestations.
- No broad website access: `activeTab` grants access only after the user invokes the extension on the current page.

## Validate

```bash
node --check background.js
node --check matcher.js
node --check autofill.js
node --check popup.js
node --test tests/*.test.mjs
```
