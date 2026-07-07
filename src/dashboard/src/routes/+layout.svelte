<script lang="ts">
	import { page } from '$app/state';
	import { getToken } from '$lib/api';
	import { onNavigate } from '$app/navigation';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		if (typeof window !== 'undefined') {
			const path = page.url.pathname;
			const token = getToken();
			if (path.startsWith('/dashboard') && !token) {
				goto('/login');
			}
		}
	});
</script>

<svelte:head>
	<title>PayPulse</title>
	<meta name="description" content="PayPulse Merchant Dashboard" />
</svelte:head>

{@render children()}
