<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();

	const siteUrl = 'https://paypulse.app';
	const siteName = 'PayPulse';
	const siteTitle = 'PayPulse — Subscription Billing & Revenue Operations';
	const siteDescription = 'All-in-one subscription billing, payments, and revenue operations for modern businesses. Manage plans, automate dunning, and scale with confidence.';
	const siteImage = `${siteUrl}/og-image.png`;
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />

	<title>{siteTitle}</title>
	<meta name="description" content={siteDescription} />
	<meta name="robots" content="index, follow" />
	<link rel="canonical" href={siteUrl} />

	<!-- Open Graph -->
	<meta property="og:type" content="website" />
	<meta property="og:url" content={siteUrl} />
	<meta property="og:title" content={siteTitle} />
	<meta property="og:description" content={siteDescription} />
	<meta property="og:image" content={siteImage} />
	<meta property="og:image:width" content="1200" />
	<meta property="og:image:height" content="630" />
	<meta property="og:site_name" content={siteName} />
	<meta property="og:locale" content="en_US" />

	<!-- Twitter / X -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:url" content={siteUrl} />
	<meta name="twitter:title" content={siteTitle} />
	<meta name="twitter:description" content={siteDescription} />
	<meta name="twitter:image" content={siteImage} />
	<meta name="twitter:site" content="@paypulse" />
	<meta name="twitter:creator" content="@paypulse" />

	<!-- App Info -->
	<meta name="application-name" content={siteName} />
	<meta name="theme-color" content="#6C3CE1" />
</svelte:head>

{@render children()}
