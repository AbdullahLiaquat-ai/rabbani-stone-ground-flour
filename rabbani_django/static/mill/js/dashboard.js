(function () {
  const scriptTag = document.currentScript;
  const csrfToken = scriptTag.getAttribute('data-csrf');

  const STATUS_COLORS = {
    'Pending': '#d4a800',
    'Milling in Progress': '#d97a26',
    'Packed': '#2f6fdb',
    'On the Way': '#e0a51c',
    'Delivered': '#1e9e5a',
  };

  const statusLabels = JSON.parse(document.getElementById('status-labels-data').textContent);
  const statusValues = JSON.parse(document.getElementById('status-values-data').textContent);
  const trendLabels = JSON.parse(document.getElementById('trend-labels-data').textContent);
  const trendRevenue = JSON.parse(document.getElementById('trend-revenue-data').textContent);
  const trendOrders = JSON.parse(document.getElementById('trend-orders-data').textContent);

  const trendCtx = document.getElementById('trendChart');
  let trendChart = null;
  if (trendCtx) {
    trendChart = new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: trendLabels,
        datasets: [
          {
            label: 'Revenue (Rs.)',
            data: trendRevenue,
            borderColor: '#1e9e5a',
            backgroundColor: 'rgba(30,158,90,0.08)',
            fill: true,
            tension: 0.35,
            yAxisID: 'y',
          },
          {
            label: 'Orders',
            data: trendOrders,
            borderColor: '#d4a800',
            backgroundColor: 'rgba(212,168,0,0.08)',
            fill: false,
            tension: 0.35,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        responsive: true,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { position: 'bottom' } },
        scales: {
          y: { type: 'linear', position: 'left', title: { display: true, text: 'Rs.' } },
          y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false }, title: { display: true, text: 'Orders' } },
        },
      },
    });
  }

  const statusCtx = document.getElementById('statusChart');
  let statusChart = null;
  if (statusCtx) {
    statusChart = new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: statusLabels,
        datasets: [{
          data: statusValues,
          backgroundColor: statusLabels.map((l) => STATUS_COLORS[l] || '#999'),
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        cutout: '68%',
        plugins: { legend: { display: false } },
      },
    });
  }

  const legendMount = document.getElementById('statusLegend');
  if (legendMount) {
    const total = statusValues.reduce((a, b) => a + b, 0) || 1;
    legendMount.innerHTML = statusLabels.map((label, i) => {
      const value = statusValues[i];
      const pct = Math.round((value / total) * 100);
      const color = STATUS_COLORS[label] || '#999';
      return `
        <div class="legend-row">
          <span><span class="legend-dot" style="background:${color}"></span>${label}</span>
          <span class="fw-600">${value} · ${pct}%</span>
        </div>`;
    }).join('');
  }

  const STATUS_BADGE_CLASS = {
    'PENDING': 'status-pending',
    'MILLING': 'status-milling',
    'PACKED': 'status-packed',
    'ON_THE_WAY': 'status-transit',
    'DELIVERED': 'status-delivered',
  };

  document.querySelectorAll('.status-update-select').forEach((select) => {
    select.addEventListener('change', function () {
      const url = this.getAttribute('data-update-url');
      const tracking = this.getAttribute('data-tracking');
      const newStatus = this.value;
      const row = document.querySelector(`tr[data-tracking="${tracking}"]`);
      const badge = row ? row.querySelector('.row-status-badge') : null;

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken,
        },
        body: `status=${encodeURIComponent(newStatus)}`,
      })
        .then((r) => r.json())
        .then((data) => {
          if (!data.ok) {
            alert(data.error || 'Could not update status.');
            return;
          }
          if (badge) {
            badge.textContent = data.status_display;
            badge.className = `status-badge row-status-badge ${STATUS_BADGE_CLASS[data.status] || 'status-pending'}`;
          }
        })
        .catch(() => alert('Network error while updating status.'));
    });
  });
})();
