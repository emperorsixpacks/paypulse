import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({ out: 'build' }),
		version: {
			name: '1.0.0'
		}
	}
};

export default config;
