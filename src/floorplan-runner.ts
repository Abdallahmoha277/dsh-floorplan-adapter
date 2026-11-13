import { spawn } from 'node:child_process'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { homedir } from 'node:os'

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
  const result = await runScript('scan.mjs', [projectPath])

  const floorplanDir = join(projectPath, 'floorplan')
  const scanJsonPath = join(floorplanDir, '.cache', 'scan.json')

  const scanRaw = await readFile(scanJsonPath, 'utf8')
  const scan = JSON.parse(scanRaw)

  return { scan, summary: result.stdout }
}

export async function runBuild(projectPath: string): Promise<{
  indexHtmlPath: string
  stdout: string
}> {
  const result = await runScript('build.mjs', [projectPath])
  const indexHtmlPath = join(projectPath, 'floorplan', 'index.html')
  return { indexHtmlPath, stdout: result.stdout }
}
