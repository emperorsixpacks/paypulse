# PayPulse — Agent Treasury

A shared USDC treasury on Arc Testnet where one funded wallet allocates hard-capped budgets to AI agents, enforced by a metering proxy.

Built with [Arc Studio](https://studio.arc.io)

---

## What it does

- **Treasury**: Anyone deposits USDC into a shared pool. The owner allocates percentage-based budgets to AI agents with configurable period lengths.
- **Hard caps**: Each agent has a per-period spending cap enforced onchain by the `PayPulse` contract. The metering proxy checks remaining budget and returns HTTP 402 when exhausted.
- **Metering proxy**: Agents make API calls through a Bun HTTP server. Each call checks the agent's budget, charges a micro-USDC fee, and batches `draw()` calls to the contract every 10 seconds.
- **Borrow policy**: Agents can request extra budget. Requests under 50% of their allocation auto-approve if funds exist. Larger requests enter a pending queue requiring 2-of-3 human approver signatures.
- **Dashboard**: Live burn progress bars, recent call feed, borrow approval queue, deposit form, and a demo simulator.

## Tech stack

- Frontend: React 18, Vite, TypeScript, Tailwind CSS, wagmi v2, ConnectKit, framer-motion
- Contract: Solidity 0.8.28, Foundry, OpenZeppelin 5.6.1 (Ownable, ReentrancyGuard, SafeERC20)
- Backend: Bun HTTP server (metering proxy)
- Chain: Arc Testnet (Chain ID 5042002) — USDC as native gas token

## Deployed contract

| Contract | Network | Address |
|---|---|---|
| PayPulse | Arc Testnet | `0xf59d0bebdfcdbf4a68505efb91abe68595819993` |

## Prerequisites

- [Bun](https://bun.sh) v1.x
- [Foundry](https://getfoundry.sh) (for contract builds)
- A browser wallet (MetaMask or similar) on Arc Testnet

## Environment variables

| Variable | Purpose | Required |
|---|---|---|
| `VITE_PAYPULSE_ADDRESS` | Deployed PayPulse contract address | Yes |
| `PROXY_PRIVATE_KEY` | Private key for the proxy wallet (must match the `proxy` address set in the contract) | Optional (simulated without it) |
| `RPC_PROXY_BASE_URL` | Arc Studio RPC proxy base URL | Optional outside Arc Studio |
| `RPC_PROXY_TOKEN` | Arc Studio RPC proxy auth token | Optional outside Arc Studio |
| `RPC_PROXY_CHAINS` | Comma-separated chain keys the proxy covers | Optional outside Arc Studio |

`VITE_PAYPULSE_ADDRESS` is already set in `.env`. Other `RPC_PROXY_*` variables are injected automatically inside Arc Studio.

## Development

```bash
bun install

# Terminal 1 — frontend (Vite)
bun run dev

# Terminal 2 — metering proxy (Bun HTTP, port 3001)
bun run server
```

The frontend proxies `/api/*` and `/proxy/*` to the backend via Vite's dev-server proxy.

## Build

```bash
bunx vite build
```

## Contract

```bash
# Build
bun run contracts:build

# Test
bun run contracts:test
```

## Demo flow

1. Connect your wallet (Arc Testnet).
2. Click **Add 3 demo agents** in the seed banner — this adds Research (40%), Scraper (30%), Support (30%) with 5-minute budget periods.
3. Start the metering proxy (`bun run server`).
4. Click **Register demo agents with proxy** in the Simulator panel.
5. Click **Start traffic** — watch budgets drain in real time.
6. Click **Exhaust Support agent** — Support hits its cap, calls start returning 402.
7. Use the borrow request flow: small borrows auto-approve; large ones appear in the **Borrow Queue** for 2-of-3 approval.

## Architecture

```
Browser → Vite proxy → Metering Proxy (port 3001)
                              ↓
                     Check budget (RPC read)
                              ↓
                     Forward or reject 402
                              ↓
                    Batch draw() to contract
                              ↓
                    PayPulse.sol on Arc Testnet
```
