<script lang="ts">
  import type { CheckoutSession } from '$lib/api';
  import { submitPayment } from '$lib/api';

  export let session: CheckoutSession;
  export let code: string;

  let name = session.customer_name || '';
  let email = session.customer_email || '';
  let cardNumber = '';
  let expiry = '';
  let cvv = '';
  let loading = false;
  let error = '';

  async function handlePay() {
    loading = true;
    error = '';
    try {
      const result = await submitPayment(code, { name, email, card_number: cardNumber, expiry, cvv });
      if (result.success && result.redirect_url) {
        window.location.href = result.redirect_url;
      } else {
        error = result.error || 'Payment failed. Please try again.';
      }
    } catch (e) {
      error = 'Something went wrong. Please try again.';
    } finally {
      loading = false;
    }
  }

  function formatCardNumber(e: Event) {
    const input = e.target as HTMLInputElement;
    cardNumber = input.value.replace(/\D/g, '').replace(/(\d{4})(?=\d)/g, '$1 ').trim();
  }
</script>

<div class="checkout-card">
  <h1>{session.plan_name}</h1>
  <p class="plan-info">Billing every {session.interval.toLowerCase()}</p>
  <div class="amount">
    &#8358;{session.amount.toLocaleString('en-NG', { minimumFractionDigits: 2 })}
    <span>/{session.interval.toLowerCase()}</span>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <form on:submit|preventDefault={handlePay}>
    <label for="name">Name</label>
    <input type="text" id="name" bind:value={name} placeholder="Your name" />

    <label for="email">Email</label>
    <input type="email" id="email" bind:value={email} placeholder="you@example.com" required />

    <label for="card">Card Number</label>
    <input
      type="text"
      id="card"
      value={cardNumber}
      on:input={formatCardNumber}
      placeholder="1234 5678 9012 3456"
      maxlength="19"
      required
    />

    <div class="row">
      <div>
        <label for="expiry">Expiry</label>
        <input type="text" id="expiry" bind:value={expiry} placeholder="MM/YY" maxlength="5" required />
      </div>
      <div>
        <label for="cvv">CVV</label>
        <input type="text" id="cvv" bind:value={cvv} placeholder="123" maxlength="4" required />
      </div>
    </div>

    <button type="submit" disabled={loading}>
      {loading ? 'Processing...' : 'Subscribe'}
    </button>
  </form>

  <p class="footer">Powered by <strong>Paypulse</strong></p>
</div>

<style>
  .checkout-card {
    background: white;
    border-radius: 12px;
    padding: 32px;
    max-width: 420px;
    width: 100%;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  }
  h1 { font-size: 20px; margin-bottom: 4px; }
  .plan-info { color: #666; margin-bottom: 24px; font-size: 14px; }
  .amount { font-size: 28px; font-weight: 700; margin-bottom: 24px; }
  .amount span { font-size: 14px; font-weight: 400; color: #666; }
  label { display: block; font-size: 13px; font-weight: 500; margin-bottom: 4px; color: #333; }
  input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 14px;
    margin-bottom: 16px;
  }
  input:focus { outline: none; border-color: #6366f1; }
  .row { display: flex; gap: 12px; }
  .row > div { flex: 1; }
  button {
    width: 100%;
    padding: 12px;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 8px;
  }
  button:hover { background: #4f46e5; }
  button:disabled { background: #a5a6f6; cursor: not-allowed; }
  .error {
    background: #fef2f2;
    color: #dc2626;
    padding: 10px 12px;
    border-radius: 8px;
    font-size: 13px;
    margin-bottom: 16px;
  }
  .footer { text-align: center; margin-top: 16px; font-size: 12px; color: #999; }
</style>
