const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export interface CheckoutSession {
  id: string;
  code: string;
  status: string;
  plan_name: string;
  amount: number;
  currency: string;
  interval: string;
  business_name: string;
  customer_email: string | null;
  customer_name: string | null;
  success_url: string;
  cancel_url: string;
  expires_at: string;
}

export interface PayResponse {
  success: boolean;
  redirect_url?: string;
  error?: string;
}

export async function fetchCheckoutSession(code: string): Promise<CheckoutSession> {
  const res = await fetch(`${API_BASE}/checkout/${code}/session`);
  if (!res.ok) throw new Error('Session not found');
  return res.json();
}

export async function submitPayment(
  code: string,
  data: {
    name: string;
    email: string;
    card_number: string;
    expiry: string;
    cvv: string;
  }
): Promise<PayResponse> {
  const res = await fetch(`${API_BASE}/checkout/${code}/pay`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}
