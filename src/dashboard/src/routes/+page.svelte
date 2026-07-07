<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getToken } from '$lib/api';

	onMount(() => {
		if (getToken()) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	});
</script>
