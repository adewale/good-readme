# Cloudflare Ecosystem README Checklist

Additional checks for projects that target the Cloudflare platform. Apply these alongside the general [quality checklist](quality-checklist.md).

## Checklist

### Deploy to Cloudflare Button

Include a one-click deploy button — this is the strongest community signal for Cloudflare projects:

```markdown
[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=<REPO_URL>)
```

The button auto-provisions KV namespaces, D1 databases, R2 buckets, and other resources by reading `wrangler.toml`. Limitation: only supports Workers apps (not Pages), only github.com and gitlab.com.

### Free-Tier Compatibility

State whether the project runs entirely on the Cloudflare free tier. The most popular community projects emphasize free-tier compatibility. If paid features are required, list them explicitly so users know the cost before they start.

Example:

```markdown
## Requirements

Runs entirely on the Cloudflare free tier. No paid plans required.
```

Or, when paid features are needed:

```markdown
## Requirements

Requires a Workers Paid plan ($5/month) for Durable Objects support. All other services used are free tier.
```

### Cloudflare Primitives Declaration

Clearly state which Cloudflare services the project uses — don't make users guess. Use a compatibility table or bulleted list:

```markdown
## Cloudflare Services

| Service          | Purpose                        |
|------------------|--------------------------------|
| Workers          | API and request handling       |
| D1               | SQLite database                |
| R2               | Asset and file storage         |
| KV               | Session and cache storage      |
| Durable Objects  | Real-time coordination         |
```

### Official Documentation Links

Link to specific pages on `developers.cloudflare.com` — not just the docs homepage. The README should serve as a gateway to official docs, not duplicate them.

Good:
- [Workers Configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
- [D1 Getting Started](https://developers.cloudflare.com/d1/get-started/)
- [R2 API Reference](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/)

Bad:
- [Cloudflare Docs](https://developers.cloudflare.com/) *(too vague)*

### Live Demo Link

Community awesome lists prioritize projects with working demos. Deploy a live instance on Workers or Pages and link to it prominently:

```markdown
## Demo

Try it live: [https://my-project.my-subdomain.workers.dev](https://my-project.my-subdomain.workers.dev)
```

If the project is an API or CLI tool without a visual demo, consider linking to an example API endpoint or a hosted playground instead.

### Maintenance Status

Indicate whether the project is actively maintained, in maintenance mode, or archived. This sets expectations for users evaluating the project:

```markdown
> **Status: Actively Maintained** — accepting PRs and responding to issues.
```

```markdown
> **Status: Maintenance Mode** — bug fixes only, no new features planned.
```

```markdown
> **Status: Archived** — no longer maintained. Fork if you need changes.
```

A maintenance badge also works:

```markdown
![Maintenance](https://img.shields.io/badge/maintenance-active-green.svg)
```

## Sources

- [Cloudflare Deploy Buttons](https://developers.cloudflare.com/workers/platform/deploy-buttons/)
- [Cloudflare Sponsorships](https://developers.cloudflare.com/sponsorships/)
- [awesome-cloudflare (zhuima)](https://github.com/zhuima/awesome-cloudflare)
- [awesome-cloudflare (irazasyed)](https://github.com/irazasyed/awesome-cloudflare)
