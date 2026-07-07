<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet" />

	<meta name="description" content="Automated invoicing, smart dunning, usage-based pricing and secure payouts — the full revenue stack behind subscriptions that just work." />
	<meta name="robots" content="index, follow" />

	<!-- Open Graph -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://paypulse.app" />
	<meta property="og:title" content="PayPulse — Billing that keeps up with you." />
	<meta property="og:description" content="Automated invoicing, smart dunning, usage-based pricing and secure payouts — the full revenue stack behind subscriptions that just work." />
	<meta property="og:image" content="https://paypulse.app/og-image.png" />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta property="og:site_name" content="PayPulse" />

	<!-- Twitter / X -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:url" content="https://paypulse.app" />
	<meta name="twitter:title" content="PayPulse — Billing that keeps up with you." />
	<meta name="twitter:description" content="Automated invoicing, smart dunning, usage-based pricing and secure payouts — the full revenue stack behind subscriptions that just work." />
	<meta name="twitter:image" content="https://paypulse.app/og-image.png" />

	<meta name="application-name" content="PayPulse" />
	<meta name="theme-color" content="#2E4CFF" />

	<title>PayPulse — Billing that keeps up with you.</title>
</svelte:head>

{@render children()}
