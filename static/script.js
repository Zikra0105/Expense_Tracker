document.addEventListener('click', function (e) {
  if (!e.target.matches('.delete-btn')) return;

  const btn = e.target;
  const id = btn.dataset.id;

  if (!confirm('Delete this expense?')) return;

  fetch('/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id: id })
  })
    .then(res => {
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res.json();
    })
    .then(data => {
      if (data.success) {
        const row = btn.closest('tr');
        row.remove();
        document.getElementById('total').textContent = '₹' + data.total;
      } else {
        alert('Delete failed: ' + (data.error || 'Unknown error'));
      }
    })
    .catch(err => {
      console.error('Delete error:', err);
      alert('Network or server error');
    });
});
