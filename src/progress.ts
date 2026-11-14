import { mkdir, writeFile } from 'node:fs/promises'
import { join } from 'node:path'

export interface Progress {
  step: string
  percent: number
  message: string
  updatedAt: string
}

export async function writeProgress(
  projectPath: string,
  step: string,
  percent: number,
  message: string,
): Promise<void> {
  const cacheDir = join(projectPath, 'floorplan', '.cache')
  const file = join(cacheDir, 'progress.json')
  const payload: Progress = {
    step,
    percent,
    message,
    updatedAt: new Date().toISOString(),
  }
  try {
    await mkdir(cacheDir, { recursive: true })
    await writeFile(file, JSON.stringify(payload, null, 2), 'utf8')
  } catch {
    // Progress is best-effort: a failed marker must never break the tool.
  }
}
