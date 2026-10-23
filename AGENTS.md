# PayPulse — Agent Treasury

> Built with Arc Studio - money-powered apps in minutes

This is the **project memory** - what Arc Studio remembers about building this app. It helps future agents (or humans) understand and extend the project.

## Deployed Contracts

| Contract | Network | Address |
|---|---|---|
| PayPulse | Arc Testnet | `0xf59d0bebdfcdbf4a68505efb91abe68595819993` |

Explorer: https://explorer.testnet.arc.io/address/0xf59d0bebdfcdbf4a68505efb91abe68595819993

Constructor args:
- `usdcToken`: `0x3600000000000000000000000000000000000000` (Arc Testnet USDC)
- `initialOwner`: `0x5B12Ce46C7194aD57d143bC22847224047b1Ef42` (platform deployer wallet)

## Architecture Notes

- Pool accounting: `poolBalance` = free (unallocated) USDC. Each agent's `allocation` is reserved from the pool at add-time and period-reset-time. `draw()` only marks reserved allocation as spent — it does NOT deduct from `poolBalance` again.
- `disburse()` is the proxy-only function that actually sends USDC to a recipient.
- Borrow auto-approves if amount ≤ 50% of allocation AND pool/lender has enough.
- Approver list is capped at exactly 3. `REQUIRED_APPROVALS = 2`.
- Demo seed uses three deterministic placeholder addresses for sandbox testing.

---

## What This App Does

[Brief description of what the app does and its primary use case]

## Tech Stack

- Frontend: React 18, Vite, TypeScript, Tailwind CSS
- Web3: wagmi v2, viem v2, ConnectKit
- Contracts: Solidity 0.8.28 + Foundry. Sources in `contracts/`, unit tests in `contracts/test/*.t.sol`. Build with `bun run contracts:build` (`forge build`), test with `bun run contracts:test` (`forge test`).
- Wallet: injected (MetaMask, etc.)
- Chain: Arc Testnet (Chain ID: 5042002, imported from `viem/chains`)
- Token: USDC (6 decimals) (Address: 0x3600000000000000000000000000000000000000, Chain: Arc Testnet)
- Toasts: Sonner

## Key Files

- `src/App.tsx` - Main application logic
- `src/components/` - UI components
- `src/config.ts` - wagmi config (chains, connectors, transports)

## To Run

```bash
bun install
bun run dev
```
