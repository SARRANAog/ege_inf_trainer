const MOJIBAKE_PATTERN = /[ÐÑÃâ]/;

function repairString(value) {
    if (typeof value !== 'string' || !MOJIBAKE_PATTERN.test(value)) {
        return value;
    }

    try {
        return decodeURIComponent(escape(value));
    } catch (error) {
        try {
            const bytes = Uint8Array.from(
                Array.from(value, (char) => char.charCodeAt(0) & 0xff)
            );
            return new TextDecoder('utf-8').decode(bytes);
        } catch {
            return value;
        }
    }
}

export function deepRepairMojibake(value) {
    if (Array.isArray(value)) {
        return value.map(deepRepairMojibake);
    }

    if (value && typeof value === 'object') {
        return Object.fromEntries(
            Object.entries(value).map(([key, innerValue]) => [
                key,
                deepRepairMojibake(innerValue),
            ])
        );
    }

    return repairString(value);
}

export function installFetchMojibakeGuard() {
    if (typeof window === 'undefined') return;
    if (window.__mojibakeGuardInstalled) return;

    const originalFetch = window.fetch.bind(window);

    window.fetch = async (...args) => {
        const response = await originalFetch(...args);
        const contentType = (response.headers.get('content-type') || '').toLowerCase();

        if (!contentType.includes('application/json')) {
            return response;
        }

        const cloned = response.clone();

        try {
            const rawText = await cloned.text();

            if (!rawText) {
                return response;
            }

            const parsed = JSON.parse(rawText);
            const repaired = deepRepairMojibake(parsed);
            const repairedText = JSON.stringify(repaired);

            const headers = new Headers(response.headers);
            headers.set('content-type', 'application/json; charset=utf-8');
            headers.delete('content-length');

            return new Response(repairedText, {
                status: response.status,
                statusText: response.statusText,
                headers,
            });
        } catch {
            return response;
        }
    };

    window.__mojibakeGuardInstalled = true;
}