---
summary: TypeScript CLI tool development — project structure, package.json bin/files setup, ESM tsconfig, Commander/yargs/citty, tsup build, prompts, terminal output, config, error handling, testing
tags: [cli, typescript, commander, tsup, esm]
related: [npm-publishing, github-actions, mcp-server]
source: synthetic-memory/typescript-cli.md
---

# CLI Tool Development in TypeScript

## Project Structure

```
my-cli/
├── src/
│   ├── index.ts          # Entry point with shebang
│   ├── commands/          # Command modules
│   ├── utils/             # Shared utilities
│   └── types.ts           # Type definitions
├── dist/                  # Compiled output
├── package.json
├── tsconfig.json
└── README.md
```

## Package.json Setup

```json
{
  "name": "my-cli",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "my-cli": "./dist/index.js"
  },
  "files": ["dist"],
  "engines": { "node": ">=18" }
}
```

The `bin` field registers the CLI command. The `files` field ensures only compiled output is published.

(Full publish checklist: [npm-publishing](npm-publishing.md#pre-publish-checklist).)

## TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "strict": true,
    "esModuleInterop": true
  },
  "include": ["src"]
}
```

For ESM output, use `"module": "NodeNext"`. Add `.js` extensions to all imports.

## Entry Point

```typescript
#!/usr/bin/env node
// src/index.ts
import { Command } from 'commander';

const program = new Command();
program
  .name('my-cli')
  .version('1.0.0')
  .description('A CLI tool');

program.command('init')
  .description('Initialize project')
  .option('-d, --dir <path>', 'target directory', '.')
  .action(async (options) => { /* ... */ });

program.parse();
```

## Argument Parsing Libraries

- **Commander.js**: Most popular. Declarative API, auto-generated help, subcommands.
- **yargs**: Rich feature set, middleware support, completion generation.
- **meow**: Minimalist, good for simple CLIs.
- **citty**: Lightweight, TypeScript-first.

## Build Pipeline

Use `tsup` for bundling (wraps esbuild):

```bash
npx tsup src/index.ts --format esm --dts --clean
```

Or plain `tsc` for simple projects. Ensure the shebang line (`#!/usr/bin/env node`) is preserved in output. Build is typically wired into `prepublishOnly` ([npm-publishing](npm-publishing.md#prepost-scripts)) and CI release jobs ([github-actions](github-actions.md#common-use-cases)).

## Interactive Prompts

Use `@inquirer/prompts` (modular) or `inquirer` (classic):

```typescript
import { input, confirm, select } from '@inquirer/prompts';
const name = await input({ message: 'Project name?' });
```

## Terminal Output

- **chalk**: Colorized output (`chalk.green('Success')`).
- **ora**: Spinner for async operations.
- **cli-table3**: Formatted tables.
- **boxen**: Boxed messages for important notices.

## Configuration Files

Read config from multiple sources with precedence:

1. CLI flags (highest)
2. Environment variables
3. Project config file (`.myrc.json`, `my.config.ts`)
4. Global config (`~/.config/my-cli/config.json`)
5. Defaults (lowest)

Use `cosmiconfig` for automatic config file discovery.

## Error Handling

Wrap the main entry in a try-catch. Use `process.exit(1)` for errors. Print user-friendly messages to stderr (`console.error`), output data to stdout.

For MCP servers (which are CLIs spawned by Claude Desktop), this stdout/stderr discipline is critical — stdout is the protocol channel. See [mcp-server](mcp-server.md#best-practices).

## Testing

Use `vitest` or `jest`. Test commands by importing action handlers directly. For integration tests, use `execa` to run the compiled CLI as a subprocess.

## Related

- [npm-publishing](npm-publishing.md) — `bin` field, `files` whitelist, and SemVer/provenance flow that publishes the CLI.
- [github-actions](github-actions.md) — release-trigger build/publish; matrix testing across Node versions.
- [mcp-server](mcp-server.md) — MCP servers are typically distributed as CLIs spawned by AI clients via the same `bin` mechanism.
