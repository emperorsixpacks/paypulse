<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { timeAgo } from '$lib/format';

	let webhooks = $state<any[]>([]);
	let loading = $state(true);
	let showCreate = $state(false);
	let form = $state({ url: '', events: '' });
	let saving = $state(false);
	let error = $state('');

	async function load() {
		loading = true;
		webhooks = await api.listWebhooks();
		loading = false;
	}

	async function create() {
		saving = true;
		error = '';
		try {
			const events = form.events.split(',').map(e => e.trim()).filter(Boolean);
			await api.createWebhook({ url: form.url, events });
			showCreate = false;
			form = { url: '', events: '' };
			await load();
		} catch (e: any) {
			error = e.message;
		} finally {
			saving = false;
		}
	}

	async function remove(id: string) {
		if (!confirm('Delete this webhook endpoint?')) return;
		await api.deleteWebhook(id);
		await load();
	}

	const availableEvents = [
		'invoice.paid', 'invoice.failed', 'subscription.created',
		'subscription.renewed', 'subscription.cancelled', 'checkout.completed',
	];

	onMount(load);
</script>

<svelte:head><title>Webhooks — PayPulse</title></svelte:head>

<div class="flex items-center justify-between mb-6">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)]">Webhooks</h2>
	<button onclick={() => showCreate = true} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
		+ Add endpoint
	</button>
</div>

{#if loading}
	<p class="text-[13px] text-slate py-12 text-center">Loading webhooks...</p>
{:else if webhooks.length === 0}
	<div class="bg-white rounded-xl border border-hair p-12 text-center">
		<p class="text-[15px] font-medium text-ink mb-2">No webhook endpoints</p>
		<p class="text-[13px] text-slate mb-6">Add an endpoint to receive real-time event notifications.</p>
		<button onclick={() => showCreate = true} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors">
			Add endpoint
		</button>
	</div>
{:else}
	<div class="space-y-3">
		{#each webhooks as wh}
			<div class="bg-white rounded-xl border border-hair p-5">
				<div class="flex items-start justify-between">
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2 mb-1">
							<span class="w-2 h-2 rounded-full {wh.is_active ? 'bg-badge-ok-text' : 'bg-badge-fail-text'}"></span>
							<p class="text-[14px] font-semibold text-ink font-[family-name:var(--font-mono)] truncate">{wh.url}</p>
						</div>
						<div class="flex items-center gap-2 mt-2 flex-wrap">
							{#each wh.events as evt}
								<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium bg-badge-neutral-bg text-badge-neutral-text">{evt}</span>
							{/each}
						</div>
						<p class="text-[12px] text-slate mt-2 font-[family-name:var(--font-mono)]">Secret: {wh.secret.slice(0, 12)}…</p>
						<p class="text-[11px] text-slate mt-1">Created {timeAgo(wh.created_at)}</p>
					</div>
					<button onclick={() => remove(wh.id)} class="text-badge-fail-text hover:opacity-70 text-[12px] font-medium shrink-0 ml-4">Delete</button>
				</div>
			</div>
		{/each}
	</div>
{/if}

{#if showCreate}
	<div class="fixed inset-0 bg-ink/40 flex items-center justify-center z-50" role="dialog" onclick={() => showCreate = false}>
		<div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 animate-fade-in" onclick={(e) => e.stopPropagation()}>
			<h3 class="text-[16px] font-bold text-ink font-[family-name:var(--font-display)] mb-5">Add webhook endpoint</h3>
			{#if error}
				<p class="text-[13px] text-badge-fail-text bg-badge-fail-bg rounded-lg px-4 py-2.5 mb-4">{error}</p>
			{/if}
			<div class="space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Endpoint URL</label>
					<input bind:value={form.url} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" placeholder="https://yourapp.com/webhooks" />
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Events (comma-separated)</label>
					<input bind:value={form.events} class="w-full h-10 px-3 bg-paper border border-hair rounded-lg text-[14px] text-ink outline-none focus:border-cobalt focus:ring-2 focus:ring-cobalt/10 transition-all" placeholder="invoice.paid, invoice.failed" />
					<p class="text-[11px] text-slate mt-1">Available: {availableEvents.join(', ')}</p>
				</div>
			</div>
			<div class="flex items-center justify-end gap-3 mt-6">
				<button onclick={() => showCreate = false} class="h-9 px-4 bg-paper border border-hair hover:bg-mist text-ink rounded-lg text-[13px] font-medium transition-colors">Cancel</button>
				<button onclick={create} disabled={saving || !form.url} class="h-9 px-4 bg-cobalt hover:bg-cobalt-dim text-white rounded-lg text-[13px] font-semibold transition-colors disabled:opacity-50">
					{saving ? 'Adding...' : 'Add endpoint'}
				</button>
			</div>
		</div>
	</div>
{/if}
