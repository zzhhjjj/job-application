(function installMatcher(global) {
  if (global.JobAutofillMatcher) return;

  const rules = [
    {
      key: "linkedin",
      patterns: [/\blinked\s*in\b/i, /linkedin\.com/i],
    },
    {
      key: "github",
      patterns: [/\bgithub\b/i, /github\.com/i],
    },
    {
      key: "email",
      autocomplete: ["email"],
      inputTypes: ["email"],
      patterns: [/\be-?mail(?: address)?\b/i, /电子邮箱|邮箱/i],
    },
    {
      key: "phone",
      autocomplete: ["tel", "tel-national"],
      inputTypes: ["tel"],
      patterns: [/\b(?:phone|mobile|telephone)(?: number)?\b/i, /手机|电话/i],
    },
    {
      key: "firstName",
      autocomplete: ["given-name"],
      patterns: [/\b(?:first|given)\s*name\b/i, /名字|名\s*\*/i],
      negative: [/preferred|nickname|middle/i],
    },
    {
      key: "lastName",
      autocomplete: ["family-name"],
      patterns: [/\b(?:last|family)\s*name\b/i, /\bsurname\b/i, /姓氏|姓\s*\*/i],
    },
    {
      key: "fullName",
      autocomplete: ["name"],
      patterns: [/\bfull(?:\s+legal)?\s*name\b/i, /^name\s*\*?$/i, /姓名/i],
      negative: [/company|employer|school|reference|native language|chinese|cyrillic|farsi/i],
    },
    {
      key: "website",
      autocomplete: ["url"],
      patterns: [/\b(?:personal\s*)?(?:website|site|portfolio)(?:\s*(?:url|link))?\b/i, /个人网站|作品集/i],
      negative: [/linkedin|github|company/i],
    },
    {
      key: "city",
      autocomplete: ["address-level2"],
      patterns: [/\bcity\b/i, /城市/i],
    },
    {
      key: "location",
      patterns: [/\b(?:your|current)\s+location\b/i, /^location\s*\*?$/i, /所在地/i],
    },
    {
      key: "state",
      autocomplete: ["address-level1"],
      patterns: [/\bstate(?:\/province)?\b/i, /\bprovince\b/i, /州|省/i],
    },
    {
      key: "country",
      autocomplete: ["country", "country-name"],
      patterns: [/\bcountry\b/i, /国家/i],
    },
  ];

  function normalize(value) {
    return String(value ?? "")
      .replace(/[_-]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function matchField({ descriptor = "", autocomplete = "", inputType = "" }) {
    const text = normalize(descriptor);
    const auto = normalize(autocomplete).toLowerCase();
    const type = normalize(inputType).toLowerCase();

    for (const rule of rules) {
      if (rule.negative?.some((pattern) => pattern.test(text))) continue;
      if (rule.autocomplete?.includes(auto)) return rule.key;
      if (rule.inputTypes?.includes(type)) return rule.key;
      if (rule.patterns.some((pattern) => pattern.test(text))) return rule.key;
    }
    return null;
  }

  global.JobAutofillMatcher = { matchField, normalize };
})(globalThis);
