import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { homedir } from 'node:os'
import { writeProgress } from './progress.js'

const FLOORPLAN_SCRIPTS_DIR = join(
  homedir(),
  'floorplan',
  'skills',
  'floorplan',
  'scripts',
)

interface ScriptResult {
  stdout: string
  stderr: string
}

function countItems(value: unknown): number {
  if (Array.isArray(value)) return value.length
  if (value && typeof value === 'object') return Object.keys(value as object).length
  return 0
}

async function runScript(scriptName: string, args: string[] = []): Promise<ScriptResult> {
  return new Promise((resolve, reject) => {
    const scriptPath = join(FLOORPLAN_SCRIPTS_DIR, scriptName)
    const child = spawn(process.execPath, [scriptPath, ...args], {
      stdio: ['ignore', 'pipe', 'pipe'],
    })

    let stdout = ''
    let stderr = ''

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString()
    })
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString()
    })

    child.on('error', (err) => {
      reject(new Error(`Failed to start ${scriptName}: ${err.message}`))
    })

    child.on('close', (code) => {
      if (code !== 0) {
        reject(
          new Error(
            `${scriptName} exited with code ${code}\n` +
              `--- stdout ---\n${stdout}\n` +
              `--- stderr ---\n${stderr}`,
          ),
        )
        return
      }
      resolve({ stdout, stderr })
    })
  })
}

export async function runScan(projectPath: string): Promise<{
  scan: unknown
  summary: string
}> {
  await writeProgress(projectPath, 'scan', 5, 'Starting scan...')

  const result = await runScript('scan.mjs', [projectPath])

  const floorplanDir = join(projectPath, 'floorplan')
  const scanJsonPath = join(floorplanDir, '.cache', 'scan.json')

  const scanRaw = await readFile(scanJsonPath, 'utf8')
  const scan = JSON.parse(scanRaw) as Record<string, unknown>

  const files = countItems(scan.files)
  const routes = countItems(scan.routes)
  await writeProgress(
    projectPath,
    'scan',
    40,
    `Scanned ${files} files, ${routes} routes; agent is writing architecture.json`,
  )

  return { scan, summary: result.stdout }
}

export async function runBuild(projectPath: string): Promise<{
  indexHtmlPath: string
  stdout: string
}> {
  await writeProgress(projectPath, 'build', 60, 'Building map...')

  const result = await runScript('build.mjs', [projectPath])
  const indexHtmlPath = join(projectPath, 'floorplan', 'index.html')

  await writeProgress(projectPath, 'done', 100, 'Map ready')

  return { indexHtmlPath, stdout: result.stdout }
}

export async function runDescribe(projectPath: string): Promise<{
  stdout: string
  worksheetsDir: string
}> {
  await writeProgress(projectPath, 'describe', 80, 'Generating description worksheets...')

  const result = await runScript('describe.mjs', [projectPath])
  const worksheetsDir = join(projectPath, 'floorplan', '.cache', 'worksheets')

  return { stdout: result.stdout, worksheetsDir }
}
