---
summary: Model Context Protocol (MCP) server development — architecture, TypeScript SDK, resources/tools/prompts, transport options, Claude Desktop config
tags: [mcp, ai, server, sdk, typescript, claude]
related: [typescript-cli, nextjs-supabase]
source: synthetic-memory/mcp-server.md
---

# Model Context Protocol (MCP) Server Development

## Overview

The Model Context Protocol (MCP) is an open standard for connecting AI assistants to external data sources and tools. An MCP server exposes resources and tools that AI clients (Claude, etc.) can discover and invoke.

## Architecture

- **Host**: The AI application (e.g., Claude Desktop).
- **Client**: Manages connections to MCP servers. One client per server.
- **Server**: Exposes resources, tools, and prompts over the protocol.
- **Transport**: Communication layer — stdio (local) or HTTP+SSE (remote).

## Server SDK (TypeScript)

```bash
npm install @modelcontextprotocol/sdk
```

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({ name: 'my-server', version: '1.0.0' }, {
  capabilities: { resources: {}, tools: {} }
});

// Define a tool
server.setRequestHandler('tools/list', async () => ({
  tools: [{
    name: 'get_weather',
    description: 'Get weather for a city',
    inputSchema: {
      type: 'object',
      properties: { city: { type: 'string' } },
      required: ['city']
    }
  }]
}));

server.setRequestHandler('tools/call', async (request) => {
  if (request.params.name === 'get_weather') {
    const city = request.params.arguments.city;
    return { content: [{ type: 'text', text: `Weather in ${city}: sunny` }] };
  }
});

// Start
const transport = new StdioServerTransport();
await server.connect(transport);
```

For packaging the server as a CLI binary (so Claude Desktop can spawn it via `command`/`args`), see [typescript-cli](typescript-cli.md).

## Resources

Resources expose data that AI can read:

```typescript
server.setRequestHandler('resources/list', async () => ({
  resources: [{
    uri: 'myapp://docs/readme',
    name: 'README',
    mimeType: 'text/markdown'
  }]
}));

server.setRequestHandler('resources/read', async (request) => ({
  contents: [{
    uri: request.params.uri,
    text: '# My App\nDocumentation here...'
  }]
}));
```

## Prompts

Prompts are reusable templates:

```typescript
server.setRequestHandler('prompts/list', async () => ({
  prompts: [{
    name: 'review_code',
    description: 'Review code for issues',
    arguments: [{ name: 'code', required: true }]
  }]
}));
```

## Transport Options

- **stdio**: Server runs as a subprocess. Best for local tools. No network setup.
- **HTTP + SSE**: Server runs as a web service. Supports remote access and authentication. Often hosted on Next.js API routes — see [nextjs-supabase](nextjs-supabase.md#data-fetching-patterns) for the routing layer.

## Client Configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/server/dist/index.js"],
      "env": { "API_KEY": "xxx" }
    }
  }
}
```

## Best Practices

- Keep tool descriptions clear and concise — the AI uses them to decide when to call the tool.
- Validate inputs with JSON Schema. Return meaningful error messages.
- Use resources for read-only data; tools for actions with side effects.
- For large datasets, implement pagination in resource responses.
- Log to stderr (not stdout) when using stdio transport, as stdout is the protocol channel.

## Related

- [typescript-cli](typescript-cli.md) — packaging the server as a `bin` entry so it can be installed and invoked via `npx` or as a Claude Desktop subprocess.
- [nextjs-supabase](nextjs-supabase.md) — when using HTTP+SSE transport, Next.js API routes are a common host with auth and middleware available.
