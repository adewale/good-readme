# Cloudflare Ecosystem README Best Practices

Guidelines for writing READMEs that are good citizens in the Cloudflare ecosystem, synthesized from analysis of official Cloudflare repositories (workers-sdk, cloudflare-docs, pingora, workerd, cloudflare-go, cf-terraforming), community projects, and Cloudflare's developer documentation.

## Cloudflare-Specific README Structure

The typical Cloudflare ecosystem README follows this structure:

1. **Project Name** (H1)
2. **One-line description** — compelling, performance-focused
3. **Badges** — minimal (npm version, CI status, license at most)
4. **Quick Start / Installation** — fastest path, multiple package managers
5. **Overview / What This Is** — 2-3 paragraphs
6. **Key Features or Packages** — bulleted or tabular
7. **Cloudflare Service Compatibility** — which products it works with
8. **Configuration** — wrangler.toml/wrangler.json patterns
9. **Documentation Links** — to developers.cloudflare.com
10. **Community / Support** — Discord, GitHub Issues, Twitter
11. **Contributing** — brief note + link to CONTRIBUTING.md
12. **License** — one line at the bottom

The philosophy: **keep the README as a concise entry point that quickly gets users started and then directs them to official documentation for depth**. Cloudflare READMEs avoid being exhaustive reference documents.

## Cloudflare-Specific Patterns

### One-Line Descriptions

Cloudflare repos lead with compelling, performance-focused one-liners:

- workers-sdk: "Deploy serverless code instantly across the globe for exceptional performance, reliability, and scale."
- pingora: "A Rust framework to build fast, reliable and programmable networked systems."
- workerd: "A JavaScript / Wasm server runtime based on the same code that powers Cloudflare Workers."

Pattern: emphasize performance, scale, and connection to Cloudflare's production infrastructure.

### Service Compatibility Declaration

Projects should clearly state which Cloudflare products they work with:

- **Workers**, **Pages**, **R2**, **D1**, **KV**, **Queues**, **Durable Objects**, **Zero Trust**, **Images**
- Use a compatibility table or bulleted list
- Example: wildebeest showcased the full stack (Workers + Pages + D1 + Durable Objects + Queues + Images + Zero Trust)

### Wrangler Configuration Documentation

- Provide example `wrangler.toml` / `wrangler.json` with placeholder values
- As of Wrangler v3.91.0, both JSON and TOML formats are supported
- Document required `compatibility_date` and `compatibility_flags`
- Show multi-environment structure (`[env.staging]`, `[env.production]`) if applicable
- Recommend `wrangler types` for generating type definitions — never hand-write `Env` interfaces

### Bindings Over REST APIs

Cloudflare strongly recommends using in-process bindings (KV, R2, D1, Queues, Durable Objects) rather than REST API calls from within Workers. Bindings require no network hop, no authentication overhead, and no extra latency. READMEs should document required bindings clearly.

### Environment Variables and Secrets

Distinguish between **vars** (non-sensitive, stored in `wrangler.toml` under `[vars]`) and **secrets** (sensitive, stored via `wrangler secret put`):

```bash
# Setting secrets
npx wrangler secret put API_TOKEN

# Or piping from environment
echo "$API_TOKEN" | npx wrangler secret put API_TOKEN
```

For local development, document the `.dev.vars` file format and remind users to add `.dev.vars` and `.env` to `.gitignore`. Secrets are non-inheritable across Wrangler environments and must be defined per environment.

### API Token Documentation

- Reference the official [Create API Token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) documentation
- Recommend account API tokens over user API keys for durable integrations
- Specify the exact permission groups (Account, Zone) and access levels (Edit vs. Read) needed
- Document recommendations for IP address filtering and TTL settings where applicable

### Linking to Official Documentation

Every Cloudflare ecosystem project should link to `developers.cloudflare.com`:

- Link to specific docs pages, not just the docs homepage
- READMEs serve as a gateway to official docs rather than duplicating them
- Reference relevant pages: Workers fundamentals, Wrangler CLI, API references, service-specific guides

### Community and Support Channels

Consistent channels across the Cloudflare ecosystem:

- **Discord**: discord.cloudflare.com (primary community channel, listed first)
- **GitHub Issues**: for bug reports and feature requests
- **GitHub Discussions**: for Q&A
- **Twitter/X**: @CloudflareDev
- **Email**: opensource@cloudflare.com (for org-level matters)

### Badge Patterns

Cloudflare repos use badges **sparingly** — no heavy badge walls. When present:

- npm version badge
- CI/build status badge
- License badge

The approach is minimalist. 2-5 badges maximum.

### Contributing Guidelines

Cloudflare uses a two-tier approach:

- **Org-level**: shared `.github/CONTRIBUTING.md` with general guidelines
- **Repo-level**: individual `CONTRIBUTING.md` for repo-specific instructions

Key conventions:
- File issues before PRs for feature requests
- Small fixes (typos, minor refactors) do not need issues
- Keep IDE config files in global `.gitignore`, not committed
- Contributor Covenant Code of Conduct enforced across all repos

READMEs say "We welcome contributions!" and link to a separate CONTRIBUTING.md rather than embedding full guidelines.

### License Patterns

- **Apache License 2.0**: infrastructure projects (pingora)
- **MIT License**: developer tools and code (workers-sdk packages)
- **Dual licensing**: cloudflare-docs uses CC-BY 4.0 for content and MIT for code
- License mentioned at the bottom of README as a brief one-liner with link to LICENSE file

## Security Considerations

Cloudflare ecosystem projects must document these security requirements:

- **Never store secrets in source code or config files** — secrets must never appear in `wrangler.toml`, `wrangler.json`, or source code
- **Use `wrangler secret put`** to store secrets encrypted at rest
- **Use `crypto.randomUUID()` or `crypto.getRandomValues()`** for security-sensitive token generation (never `Math.random()`)
- **Use `crypto.subtle.timingSafeEqual()`** when comparing secrets
- **Avoid global mutable state** — Workers reuse isolates across requests, so module-level mutable variables cause cross-request data leaks
- **Stream large payloads** — use `TransformStream` and `pipeTo` to stay within the 128 MB memory limit
- **Avoid `passThroughOnException()`** — use explicit try/catch blocks instead

## Account and Resource Setup

READMEs should document:

- Instructions to create a Cloudflare account and note which plan tier is needed
- Steps to create required resources (D1 databases, KV namespaces, R2 buckets) with IDs copied into Wrangler config
- How to set `account_id` in `wrangler.toml`/`wrangler.json` or as a GitHub Action input
- Local development setup using `.dev.vars` for secrets
- Include a `.dev.vars.example` file in the repo (dotenv format) documenting required secrets without exposing values

## Deployment Patterns

Three tiers of deployment documentation:

### Tier 1 — One-Click Deploy Button (recommended)

Cloudflare provides an official "Deploy to Cloudflare" button that auto-provisions KV namespaces, D1 databases, R2 buckets, and other resources by reading `wrangler.toml`:

```markdown
[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=<YOUR_GIT_REPO_URL>)
```

Limitation: only supports Workers apps (not Pages), only github.com and gitlab.com.

### Tier 2 — CLI Deployment

```bash
npm create cloudflare@latest  # scaffold new project
npm install
# configure wrangler.toml
wrangler deploy
```

For Pages: `wrangler pages deploy`.

Include dry-run verification: `npx wrangler deploy --dry-run --outdir dist`.

### Tier 3 — CI/CD with GitHub Actions

Uses `cloudflare/wrangler-action@v3` with `CLOUDFLARE_API_TOKEN` and `accountId` stored as GitHub secrets. Warn against storing API tokens in the repository.

## Testing Documentation

- Recommend `@cloudflare/vitest-pool-workers` for testing inside the actual Workers runtime with real bindings
- Note that the Vitest pool auto-injects `nodejs_compat`, so `wrangler.jsonc` should explicitly include the flag if code depends on Node.js built-ins
- Show example test setup and commands

## Monorepo Patterns

For monorepos (like workers-sdk), use a table or list to describe sub-packages:

| Package | Purpose |
|---------|---------|
| wrangler | CLI for building Workers |
| create-cloudflare (C3) | App creation and deployment |
| miniflare | Local development simulator |

## Design Philosophy Sections

Larger infrastructure projects should include design principles:

- pingora: "Who should consider Pingora" section with specific use cases
- workerd: Six core design principles (server-first, standards-based, nanoservices, etc.)
- Include production scale proof points where applicable (e.g., "over 40 million requests per second")

## Platform Support

Technical projects should specify:

- Supported platforms (Linux tier 1, macOS, Windows)
- Supported architectures (x86_64, aarch64)
- Minimum language/runtime versions
- Build dependencies
- Use tabular format with tier distinctions when applicable

## Trademark Guidelines

Cloudflare's trademark rules are strict and explicit for third-party projects:

- **Never use "Cloudflare" as part of a product or brand name**, joined with a hyphen, or in app names
- Use referential phrases instead: "runs on," "for use with," "for," or "compatible with"
- Never imply Cloudflare affiliation, endorsement, or sponsorship without written permission
- Always capitalize "Cloudflare" and never alter its spelling
- Do not use Cloudflare trademarks in domain names, meta tags, or SEO keywords
- If using Cloudflare marks with permission, include attribution: "Cloudflare, the Cloudflare logo, and Cloudflare Workers are trademarks and/or registered trademarks of Cloudflare, Inc."

Source: [Cloudflare Trademark Guidelines](https://www.cloudflare.com/trademark/)

## What Makes a "Good Citizen"

A Cloudflare ecosystem project is a good citizen when its README:

1. **Clearly states which Cloudflare services it uses** — don't make users guess
2. **Links to official docs rather than duplicating them** — reduce maintenance burden and ensure accuracy
3. **Provides working wrangler config examples** — with placeholder values, not real credentials
4. **Documents the fastest path from zero to running** — `npm create cloudflare@latest` or equivalent
5. **Separates secrets from configuration** — `.dev.vars` for local, `wrangler secret put` for production
6. **Specifies compatibility requirements** — `compatibility_date`, `compatibility_flags`, Node.js version
7. **Uses bindings, not REST APIs** — and documents binding configuration
8. **Points to Discord for community support** — the primary Cloudflare community channel
9. **Follows the minimalist badge convention** — 2-5 badges, no badge walls
10. **Keeps the README as an entry point** — not an exhaustive reference; link to deeper docs
11. **Includes a Deploy to Cloudflare button** — one-click deployability is the strongest community signal
12. **Provides a live demo link** — community awesome lists highlight projects with working demos
13. **Works within the free tier** — the most popular community projects emphasize free-tier compatibility
14. **Shows maintenance status** — indicate whether the project is actively maintained, in maintenance mode, or archived
15. **Respects Cloudflare trademarks** — use "compatible with Cloudflare Workers," never "Cloudflare-MyApp"

## Sources

- [Cloudflare GitHub Organization](https://github.com/cloudflare)
- [Cloudflare Open Source Portal](https://cloudflare.github.io/)
- [Cloudflare Docs CONTRIBUTING.md](https://github.com/cloudflare/cloudflare-docs/blob/production/CONTRIBUTING.md)
- [Cloudflare Style Guide](https://developers.cloudflare.com/style-guide/)
- [Workers Best Practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
- [Secrets Documentation](https://developers.cloudflare.com/workers/configuration/secrets/)
- [Environment Variables Documentation](https://developers.cloudflare.com/workers/configuration/environment-variables/)
- [Wrangler Configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
- [Create API Token](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)
- [3rd Party Integrations](https://developers.cloudflare.com/workers/databases/third-party-integrations/)
- [Cloudflare Sponsorships](https://developers.cloudflare.com/sponsorships/)
- [Make a README](https://www.makeareadme.com/)
- [Standard Readme Specification](https://github.com/RichardLitt/standard-readme/blob/main/spec.md)
- [Cloudflare Trademark Guidelines](https://www.cloudflare.com/trademark/)
- [Deploy to Cloudflare Buttons](https://developers.cloudflare.com/workers/platform/deploy-buttons/)
- [awesome-cloudflare (zhuima)](https://github.com/zhuima/awesome-cloudflare)
- [awesome-cloudflare (irazasyed)](https://github.com/irazasyed/awesome-cloudflare)
- [awesome-cloudflare-workers (lukeed)](https://github.com/lukeed/awesome-cloudflare-workers)
