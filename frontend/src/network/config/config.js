const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000/";

function normalizeBaseUrl(url) {
    const base = (url || DEFAULT_API_BASE_URL).trim();
    return base.endsWith("/") ? base : `${base}/`;
}

const config = {
    API_BASE_URL: normalizeBaseUrl(process.env.NEXT_PUBLIC_API_BASE_URL),

    API_TIMEOUT: 30000,

    DEFAULT_HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },

    API_VERSION: 'v1',

    MAX_RETRIES: 3,
    RETRY_DELAY: 1000,
};

export default config;
