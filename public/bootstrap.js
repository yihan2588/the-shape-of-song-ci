(() => {
  'use strict';
  const panel = document.getElementById('app-state');
  const message = document.getElementById('load-message');
  const retry = document.getElementById('retry-load');
  let loading = false;

  function validate(data) {
    const n = data?.documents?.length;
    if (!n || data.neighbors?.length !== n) throw new Error('Incomplete dataset');
    for (const view of ['tsne', 'umap']) {
      if (data.coordinates?.[view]?.length !== n
          || data.coordinates[view].some(row => row.length !== 2 || !row.every(Number.isFinite))) {
        throw new Error('Invalid map coordinates');
      }
    }
    if (data.neighbors.some((rows, i) => rows.length !== 3
        || rows.some(row => !Number.isInteger(row.index) || row.index < 0
          || row.index >= n || row.index === i || !Number.isFinite(row.cosine)))) {
      throw new Error('Invalid nearest poems');
    }
    return data;
  }

  async function load() {
    if (loading) return;
    loading = true;
    retry.hidden = true;
    message.textContent = 'Loading poems… / 正在加载词作…';
    try {
      const result = await fetch('/api/atlas', { signal: AbortSignal.timeout(30000) });
      if (!result.ok) throw new Error('Database unavailable');
      window.POETRY_DATA = validate(await result.json());
      await new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = '/app.js';
        script.onload = resolve;
        script.onerror = reject;
        document.body.append(script);
      });
      document.querySelector('main').setAttribute('aria-busy', 'false');
      panel.hidden = true;
    } catch {
      message.textContent = 'Could not load the poems. Please retry. / 词作加载失败，请重试。';
      retry.hidden = false;
    } finally {
      loading = false;
    }
  }
  retry.addEventListener('click', load);
  load();
})();
