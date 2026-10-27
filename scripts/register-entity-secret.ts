/**
 * One-time Circle entity secret registration.
 * Run with: bun run scripts/register-entity-secret.ts
 * NEVER run this twice — it replaces the registered secret and invalidates the old recovery file.
 */
import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'
import { registerEntitySecretCiphertext } from '@circle-fin/developer-controlled-wallets'
import { initiateDeveloperControlledWalletsClient } from '@circle-fin/developer-controlled-wallets'

const apiKey = process.env.CIRCLE_API_KEY
if (!apiKey) {
  console.error('CIRCLE_API_KEY is not set')
  process.exit(1)
}

// 1. Generate secret — captured in memory, never printed
const entitySecret = crypto.randomBytes(32).toString('hex')

// 2. Register with Circle
const recoveryDir = '/home/user/app/.circle'
fs.mkdirSync(recoveryDir, { recursive: true })

console.log('Registering entity secret with Circle...')
const response = await registerEntitySecretCiphertext({
  apiKey,
  entitySecret,
  recoveryFileDownloadPath: recoveryDir,
})

const recoveryPath = path.join(recoveryDir, 'recovery_file.dat')
if (response.data?.recoveryFile) {
  fs.writeFileSync(recoveryPath, response.data.recoveryFile)
}

// 3. Persist to .env
const envPath = '/home/user/app/.env'
fs.appendFileSync(envPath, `\nCIRCLE_ENTITY_SECRET=${entitySecret}\n`, 'utf-8')

// 4. Verify
console.log('Verifying registration...')
const client = initiateDeveloperControlledWalletsClient({ apiKey, entitySecret })
await client.listWalletSets({ pageSize: 1 })

console.log('SUCCESS: Entity secret registered and verified.')
console.log('Recovery file written to:', recoveryPath)
console.log('CIRCLE_ENTITY_SECRET written to .env')
