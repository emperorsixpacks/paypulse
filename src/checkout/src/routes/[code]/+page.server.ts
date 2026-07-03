import type { PageServerLoad } from './$types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const load: PageServerLoad = async ({ params }) => {
  const { code } = params;

  try {
    const res = await fetch(`${API_BASE}/checkout/${code}/session`);
    if (!res.ok) {
      return { status: 404, error: 'Checkout not found' };
    }
    const session = await res.json();
    return { session, code };
  } catch {
    return { status: 500, error: 'Failed to load checkout' };
  }
};
