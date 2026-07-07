<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let keys = $state<any[]>([]);
	let loading = $state(true);
	let showCreate = $state(false);
	let form = $state({ name: '', is_live: false });
	let saving = $state(false);
	let error = $state('');
	let newKey = $state('');

	async function load() {
		loading = true;
		keys = await api.listApiKeys();
		loading = false;
	}

	async function create() {
		saving = true;
		error = '';
		try {
			const result = await api.createApiKey(form.name, form.is_live);
			newKey = result.key || result.api_key || '';
			showCreate = false;
			await load();
		} catch (e: any) {
			error = e.message;
		} finally {
			saving = false;
		}
	}

	function copyKey() {
		navigator.clipboard.writeText(newKey);
	}

	function revoke(id: string) {
		if (!confirm('Revoke this API key? This cannot be undone.')) return;
		api.revokeApiKey(id).then(load);
	}

	onMount(load);
</script>

<svelte:head><title>Developers — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">API keys</h2>
	<button onclick={() => { showCreate = true; newKey = ''; }} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
		+ Create key
	</button>
</div>

{#if newKey}
	<div class="bg-badge-ok-bg border border-badge-ok-text/20 rounded-xl p-5 mb-6">
		<p class="text-[13px] font-semibold text-badge-ok-text mb-2">New API key created</p>
		<p class="text-[13px] text-ink mb-3">Copy this key now. It won't be shown again.</p>
		<div class="flex items-center gap-2">
			<code class="flex-1 h-10 px-3 bg-white border border-hair rounded-lg text-[13px] text-ink font-[family-name:var(--font-mono)] flex items-center truncate">{newKey}</code>
			<button onclick={copyKey} class="h-10 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors shrink-0">Copy</button>
		</div>
	</div>
{/if}

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading API keys...</p>
{:else if keys.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No API keys</p>
		<p class="text-[13px] text-slate mb-6">Create an API key to authenticate requests to the PayPulse API.</p>
		<button onclick={() => showCreate = true} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
			Create key
		</button>
	</div>
{:else}
	<div class="bg-white rounded-xl border border-hair overflow-hidden">
		<table class="w-full text-[13px]">
			<thead>
				<tr class="text-left text-[11px] font-medium text-slate uppercase tracking-wider border-b border-hair">
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Name</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Key prefix</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Environment</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]">Status</th>
					<th class="px-5 py-3 font-[family-name:var(--font-mono)]"></th>
				</tr>
			</thead>
			<tbody class="divide-y divide-hair/50">
				{#each keys as k}
					<tr class="hover:bg-paper transition-colors">
						<td class="px-5 py-3 font-semibold text-ink">{k.name}</td>
						<td class="px-5 py-3 font-[family-name:var(--font-mono)] text-[12px] text-slate">{k.key_prefix}…</td>
						<td class="px-5 py-3">
							<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {k.is_live ? 'bg-badge-fail-bg text-badge-fail-text' : 'bg-badge-wait-bg text-badge-wait-text'}">
								{k.is_live ? 'LIVE' : 'TEST'}
							</span>
						</td>
						<td class="px-5 py-3">
							<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold bg-badge-ok-bg text-badge-ok-text">Active</span>
						</td>
						<td class="px-5 py-3 text-right">
							<button onclick={() => revoke(k.id)} class="text-badge-fail-text hover:opacity-70 text-[12px] font-medium">Revoke</button>
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
			<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-5">Create API key</h3>
			{#if error}
				<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5 mb-4">{error}</p>
			{/if}
			<div class="space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Name</label>
					<input bind:value={form.name} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" placeholder="e.g. Production key" />
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Environment</label>
					<div class="flex gap-2">
						<button
							type="button"
							onclick={() => form.is_live = false}
							class="h-10 px-4 rounded-lg border text-[13px] font-medium transition-colors
								{!form.is_live ? 'border-cobalt bg-cobalt/5 text-cobalt' : 'border-hair bg-paper text-slate hover:border-cobalt/40'}"
						>Test</button>
						<button
							type="button"
							onclick={() => form.is_live = true}
							class="h-10 px-4 rounded-lg border text-[13px] font-medium transition-colors
								{form.is_live ? 'border-badge-fail-text bg-badge-fail-bg text-badge-fail-text' : 'border-hair bg-paper text-slate hover:border-cobalt/40'}"
						>Live</button>
					</div>
				</div>
			</div>
			<div class="flex items-center justify-end gap-3 mt-6">
				<button onclick={() => showCreate = false} class="h-9 px-4 bg-paper border border-hair hover:bg-mist text-ink rounded-lg text-[13px] font-medium transition-colors">Cancel</button>
				<button onclick={create} disabled={saving || !form.name} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors disabled:opacity-50">
					{saving ? 'Creating...' : 'Create'}
				</button>
			</div>
		</div>
	</div>
{/if}
