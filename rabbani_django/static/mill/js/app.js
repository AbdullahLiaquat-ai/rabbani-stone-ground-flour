(function () {
  const scriptTag = document.currentScript;
  const trackUrl = scriptTag.getAttribute('data-track-url');
  const estimateUrl = scriptTag.getAttribute('data-estimate-url');

  function statusPillClass(statusCode) {
    return {
      PENDING: 'status-pending',
      MILLING: 'status-milling',
      PACKED: 'status-packed',
      ON_THE_WAY: 'status-transit',
      DELIVERED: 'status-delivered',
    }[statusCode] || 'status-pending';
  }

  const trackBtn = document.getElementById('trackBtn');
  const trackInput = document.getElementById('trackingInput');
  const trackResult = document.getElementById('trackingResult');

  function runTrack() {
    const id = trackInput.value.trim();
    if (!id) {
      trackResult.innerHTML = '<span style="color:#b02a37;">Please enter an Order ID</span>';
      return;
    }
    trackResult.innerHTML = '<span class="text-muted">Looking up your order…</span>';
    fetch(`${trackUrl}?id=${encodeURIComponent(id)}`)
      .then((r) => r.json())
      .then((data) => {
        if (!data.found) {
          trackResult.innerHTML = `<span style="color:#b02a37;">${data.error}</span>`;
          return;
        }
        trackResult.innerHTML = `
          <div style="background:var(--yellow-light); padding:12px 18px; border-radius:20px;">
            <div class="fw-800 tracking-mono">${data.tracking_number}</div>
            <div class="small text-muted mt-1">${data.product} · ${data.weight_kg} kg · ${data.city}</div>
            <span class="status-badge ${statusPillClass(data.status_code)} mt-2 d-inline-block">${data.status}</span>
          </div>`;
      })
      .catch(() => {
        trackResult.innerHTML = '<span style="color:#b02a37;">Something went wrong. Please try again.</span>';
      });
  }

  if (trackBtn) {
    trackBtn.addEventListener('click', runTrack);
    trackInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') runTrack(); });
  }

  const calcOrigin = document.getElementById('calcOrigin');
  const calcDest = document.getElementById('calcDest');
  const calcResult = document.getElementById('calcResult');

  function runEstimate() {
    const origin = calcOrigin.value;
    const destination = calcDest.value;
    if (!origin || !destination) {
      calcResult.innerHTML = 'Select both cities for an estimate.';
      return;
    }
    fetch(`${estimateUrl}?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`)
      .then((r) => r.json())
      .then((data) => {
        calcResult.innerHTML = data.ok
          ? `💰 ${data.message}`
          : data.message;
      })
      .catch(() => {
        calcResult.innerHTML = 'Could not calculate estimate right now.';
      });
  }

  if (calcOrigin && calcDest) {
    calcOrigin.addEventListener('change', runEstimate);
    calcDest.addEventListener('change', runEstimate);
  }
})();
