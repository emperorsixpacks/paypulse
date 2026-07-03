<script lang="ts">
  import CheckoutForm from '$lib/components/CheckoutForm.svelte';

  export let data;
</script>

<svelte:head>
  <title>Checkout - Paypulse</title>
</svelte:head>

<main>
  {#if data.error}
    <div class="error-state">
      <h1>{data.error}</h1>
      <p>This checkout link may have expired or does not exist.</p>
    </div>
  {:else}
    <CheckoutForm session={data.session} code={data.code} />
  {/if}
</main>

<style>
  main {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f5f5f5;
    padding: 20px;
  }
  .error-state {
    text-align: center;
    color: #666;
  }
  .error-state h1 {
    font-size: 20px;
    margin-bottom: 8px;
    color: #333;
  }
</style>
