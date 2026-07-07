<script lang="ts">
	import { onMount } from 'svelte';
	import { api, clearToken, clearApiKey } from '$lib/api';
	import { goto } from '$app/navigation';

	let merchant = $state<any>(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			merchant = await api.getMe();
		} catch {
			goto('/login');
		} finally {
			loading = false;
		}
	});

	function logout() {
		clearToken();
		clearApiKey();
		goto('/login');
	}
</script>

<svelte:head><title>Settings — PayPulse</title></svelte:head>

<div class="max-w-2xl">
	<h2 class="text-[20px] font-bold text-ink font-[family-name:var(--font-display)] mb-6">Settings</h2>

	{#if loading}
		<p class="text-[13px] text-slate py-8 text-center">Loading...</p>
	{:else if merchant}
		<!-- Profile -->
		<div class="bg-white rounded-xl border border-hair mb-6">
			<div class="px-5 py-4 border-b border-hair">
				<h3 class="text-[14px] font-semibold text-ink">Profile</h3>
			</div>
			<div class="p-5 space-y-4">
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Email</label>
					<p class="text-[14px] text-ink">{merchant.email}</p>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Business name</label>
					<p class="text-[14px] text-ink">{merchant.business_name}</p>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Member since</label>
					<p class="text-[14px] text-ink">{new Date(merchant.created_at).toLocaleDateString()}</p>
				</div>
				<div>
					<label class="block text-[12px] font-medium text-slate mb-1.5">Status</label>
					<span class="inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold {merchant.is_active ? 'bg-badge-ok-bg text-badge-ok-text' : 'bg-badge-fail-bg text-badge-fail-text'}">
						{merchant.is_active ? 'Active' : 'Inactive'}
					</span>
				</div>
			</div>
		</div>

		<!-- Danger zone -->
		<div class="bg-white rounded-xl border border-badge-fail-text/20">
			<div class="px-5 py-4 border-b border-badge-fail-text/20">
				<h3 class="text-[14px] font-semibold text-badge-fail-text">Danger zone</h3>
			</div>
			<div class="p-5 flex items-center justify-between">
				<div>
					<p class="text-[13px] text-ink font-medium">Sign out</p>
					<p class="text-[12px] text-slate">Sign out of your PayPulse account.</p>
				</div>
				<button onclick={logout} class="h-9 px-4 bg-badge-fail-text hover:opacity-90 text-white rounded-lg text-[13px] font-semibold transition-colors">
					Sign out
				</button>
			</div>
		</div>
	{/if}
</div>
