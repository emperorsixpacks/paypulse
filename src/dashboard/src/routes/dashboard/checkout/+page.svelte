<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { formatStatus, timeAgo } from '$lib/format';

	let sessions = $state<any[]>([]);
	let plans = $state<any[]>([]);
	let loading = $state(true);
	let showCreate = $state(false);
	let form = $state({ plan_id: '', success_url: 'https://example.com/success', cancel_url: 'https://example.com/cancel' });
	let saving = $state(false);
	let error = $state('');
	let copiedCode = $state('');

	async function load() {
		loading = true;
		const [s, p] = await Promise.all([api.listCheckoutSessions(), api.listPlans()]);
		sessions = s;
		plans = p;
		loading = false;
	}

	async function create() {
		saving = true;
		error = '';
		try {
			const result = await api.createCheckoutSession(form);
			showCreate = false;
			await load();
			copyLink(result.code);
		} catch (e: any) {
			error = e.message;
		} finally {
			saving = false;
		}
	}

	function copyLink(code: string) {
		const url = `${window.location.origin}/checkout/${code}`;
		navigator.clipboard.writeText(url);
		copiedCode = code;
		setTimeout(() => copiedCode = '', 2000);
	}

	onMount(load);
</script>

<svelte:head><title>Checkout — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Checkout sessions</h2>
	<button onclick={() => showCreate = true} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
		+ New session
	</button>
</div>

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading checkout sessions...</p>
{:else if sessions.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No checkout sessions</p>
		<p class="text-[13px] text-slate mb-6">Create a session to share a checkout link with a customer.</p>
		<button onclick={() => showCreate = true} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
			Create session
		</button>
	</div>
{:else}
	<div class="bg-white rounded-xl border border-hair overflow-hidden">
		<table class="w-full text-[13px]">
			<thead>
				<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Code</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Plan</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Expires</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Created</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]"></th>
				</tr>
			</thead>
			<tbody class="divide-y divide-hair/50">
				{#each sessions as sess}
					{@const s = formatStatus(sess.status)}
					<tr class="hover:bg-paper transition-colors">
						<td class="px-5 py-3 font-[family-name:var(--font-mono)] text-[12px] text-ink">{sess.code}</td>
						<td class="px-5 py-3 text-slate">{sess.plan_id.slice(0, 8)}…</td>
						<td class="px-5 py-3">
							<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {s.bgClass} {s.textClass}">{s.label}</span>
						</td>
						<td class="px-5 py-3 text-slate text-[12px]">{new Date(sess.expires_at).toLocaleString()}</td>
						<td class="px-5 py-3 text-slate text-[12px]">{timeAgo(sess.created_at)}</td>
						<td class="px-5 py-3 text-right">
							<div class="flex items-center justify-end gap-2">
								<button onclick={() => copyLink(sess.code)} class="text-cobalt hover:text-cobalt-dim text-[12px] font-medium">
									{copiedCode === sess.code ? 'Copied!' : 'Copy link'}
								</button>
								<button onclick={() => { if (confirm('Cancel this session?')) api.cancelCheckoutSession(sess.code).then(load); }} class="text-badge-fail-text hover:opacity-70 text-[12px] font-medium">Cancel</button>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

{#if showCreate}
	<div class="fixed inset-0 bg-ink/40 flex items-center justify-center z-50" role="dialog" onclick={() => showCreate = false}>
		<div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 animate-fade-in" onclick={(e) => e.stopPropagation()}>
			<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-5">Create checkout session</h3>
			{#if error}
				<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5 mb-4">{error}</p>
			{/if}
			<div class="space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Plan</label>
					<select bind:value={form.plan_id} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all">
						<option value="">Select a plan</option>
						{#each plans as p}
							<option value={p.id}>{p.name} — {p.amount} {p.currency}</option>
						{/each}
					</select>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Success URL</label>
					<input bind:value={form.success_url} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Cancel URL</label>
					<input bind:value={form.cancel_url} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" />
				</div>
			</div>
			<div class="flex items-center justify-end gap-3 mt-6">
				<button onclick={() => showCreate = false} class="h-9 px-4 bg-paper border border-hair hover:bg-mist text-ink rounded-lg text-[13px] font-medium transition-colors">Cancel</button>
				<button onclick={create} disabled={saving || !form.plan_id} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors disabled:opacity-50">
					{saving ? 'Creating...' : 'Create'}
				</button>
			</div>
		</div>
	</div>
{/if}
