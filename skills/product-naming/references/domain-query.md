# Domain Query Reference

Use this file only when a naming task requires domain availability or price checks.

## RDAP Availability

RDAP is good for registered/not-found checks. It does not return checkout pricing.

Common endpoints:

- `.com`: `https://rdap.verisign.com/com/v1/domain/<domain>`
- Other TLDs: `https://rdap.org/domain/<domain>`

Interpretation:

- HTTP 200 with `objectClassName: "domain"` means registered.
- HTTP 404 or a body saying not found/not registered means likely available.
- Save registrar and registration date when present; they help explain why a strong `.com` is unavailable.

Batch-check pattern:

```bash
node - <<'NODE'
const names = ['candidateone', 'candidatetwo', 'candidatethree'];
const tlds = ['com', 'design', 'art'];

async function check(domain) {
  const tld = domain.split('.').pop();
  const url = tld === 'com'
    ? `https://rdap.verisign.com/com/v1/domain/${domain}`
    : `https://rdap.org/domain/${domain}`;
  const res = await fetch(url, { redirect: 'follow' });
  const text = await res.text();
  let data = null;
  try { data = JSON.parse(text); } catch {}
  const available = res.status === 404 || /not found|object not found|domain not found|not registered/i.test(text);
  const registrar = data?.entities?.find((entity) => entity.roles?.includes('registrar'))?.vcardArray?.[1]?.find((field) => field[0] === 'fn')?.[3] || '';
  const registration = data?.events?.find((event) => event.eventAction === 'registration')?.eventDate || '';
  return { domain, available, registered: res.ok && data?.objectClassName === 'domain', registrar, registration };
}

(async () => {
  for (const name of names) {
    const row = [];
    for (const tld of tlds) {
      row.push(await check(`${name}.${tld}`));
      await new Promise((resolve) => setTimeout(resolve, 80));
    }
    console.log(JSON.stringify({ name, row }));
  }
})();
NODE
```

## Tencent Cloud CheckDomain

Use Tencent Cloud when exact registration price matters for Tencent Cloud purchase decisions.

Endpoint:

- Host: `domain.tencentcloudapi.com`
- Action: `CheckDomain`
- Version: `2018-08-08`
- Required parameter: `DomainName`
- Useful parameter: `Period: "1"` because empty `Period` may fail to price premium names.

Important response fields:

- `Available`: whether the domain can be registered.
- `Premium`: whether it is a premium word.
- `Price`, `RealPrice`: registration price signals.
- `FeeRenew`, `FeeTransfer`, `FeeRestore`: follow-on costs.
- `Reason`, `BlackWord`, `RecordSupport`: constraints to surface when present.

Do not call this endpoint as an unsigned raw POST and treat errors as domain results. If credentials or `tccli` are missing, state that Tencent Cloud pricing could not be verified.

## Public Registrar Reference Pricing

Use public registrar pricing only as a fallback reference for non-premium TLD baseline cost.

For Porkbun, the pricing page currently exposes per-TLD fields such as:

- `data-extension="com" data-price-registration="1108"`
- `data-extension="design" data-price-registration="1081" data-price-renewal="4686"`
- `data-extension="art" data-price-registration="360" data-price-renewal="2111"`

These are cents and should be reported as non-premium reference prices with the source and date queried. They are not a substitute for Tencent Cloud `RealPrice`.
