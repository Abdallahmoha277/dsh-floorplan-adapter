import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import { runScan, runBuild, runDescribe } from './floorplan-runner.js'

export const name = 'floorplan-adapter'
export const inject = ['tools']

const SCAN_INSTRUCTIONS = `
You have just scanned a project. The summary above lists files, imports, and HTTP routes.

NEXT STEP: Write \`floorplan/architecture.json\` in the project root.

The file must follow this schema exactly:

{
  "schema": "floorplan/architecture@1",
  "summary": "<one-paragraph description of what this codebase does>",
  "subsystems": [
    {
      "id": "<kebab-case-id>",
      "name": "<human readable name>",
      "description": "<one sentence>",
      "modules": [
        {
          "id": "<kebab-case-id>",
          "name": "<human readable name>",
          "description": "<one sentence>",
          "files": ["<path/relative/to/project/root>", "..."]
        }
      ]
    }
  ],
  "flows": [
    {
      "id": "<kebab-case-id>",
      "name": "<human readable name>",
      "description": "<one sentence>",
      "steps": ["<short step description>", "..."]
    }
  ]
}

Rules:
- Every file from the scan should be assigned to exactly one module.
- Group files by subsystem first (e.g. "api", "data", "ui"), then by module within each subsystem.
- Keep descriptions short and concrete. Avoid jargon.
- Use relative paths from the project root, without leading "./".

After writing architecture.json, call floorplan_build to generate the map.
`

const DESCRIBE_INSTRUCTIONS = `
You have just generated description worksheets. 

NEXT STEPS:
1. Use your file reading tools to read the worksheet files in the directory provided above.
2. For each worksheet, write a corresponding JSON file in \`floorplan/descriptions/\` (e.g., if you read \`api.md\`, write \`floorplan/descriptions/api.json\`).
3. The JSON file must follow this schema exactly:
{
  "files": {
    "path/to/file.ts": {
      "name": "A short 2-5 word title",
      "description": "One sentence explaining what this file does, starting with a verb."
    }
  },
  "routes": {
    "GET /api/example": {
      "name": "Short title",
      "description": "One sentence explaining what this endpoint does."
    }
  }
}
4. Keep names and descriptions in plain, simple language. Avoid jargon.
5. After writing the JSON files, call \`floorplan_build\` again to apply the descriptions to the map.
`

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'floorplan_scan',
    description: 'Scans a project directory and returns a compact summary of files, imports, and HTTP routes. After calling this, read the summary, write floorplan/architecture.json in the project, then call floorplan_build to generate the map.',
    parameters: {
      projectPath: {
        type: 'string',
        required: true,
        description: 'Absolute path to the project root to scan.',
      },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const { summary } = await runScan(args.projectPath)
      return `${summary}\n\n${SCAN_INSTRUCTIONS}`
    },
  }))

  ctx.tools.register(defineTool({
    name: 'floorplan_build',
    description: 'Builds the interactive map from floorplan/architecture.json. Requires that architecture.json already exists in the project. Returns the path to the generated index.html.',
    parameters: {
      projectPath: {
        type: 'string',
        required: true,
        description: 'Absolute path to the project root.',
      },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const { indexHtmlPath, stdout } = await runBuild(args.projectPath)
      return `Map built successfully.\n\nindex.html: ${indexHtmlPath}\n\nBuild output:\n${stdout}`
    },
  }))

  ctx.tools.register(defineTool({
    name: 'floorplan_describe',
    description: 'Generates description worksheets for the current map. Read the worksheets, write JSON files in floorplan/descriptions/, then call floorplan_build again.',
    parameters: {
      projectPath: {
        type: 'string',
        required: true,
        description: 'Absolute path to the project root.',
      },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const { stdout, worksheetsDir } = await runDescribe(args.projectPath)
      return `Worksheets directory: ${worksheetsDir}\n\n${stdout}\n\n${DESCRIBE_INSTRUCTIONS}`
    },
  }))
}
