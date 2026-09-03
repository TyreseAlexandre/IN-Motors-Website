function previewPhotos(input) {
  const grid = document.getElementById('photoPreview');
  if (!grid) return;
  grid.innerHTML = '';
  const files = Array.from(input.files || []).slice(0, 12);
  files.forEach(file => {
    if (!file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = e => {
      const img = document.createElement('img');
      img.src = e.target.result;
      img.alt = file.name;
      grid.appendChild(img);
    };
    reader.readAsDataURL(file);
  });
}

(function setupConfirmDialogs() {
  const overlay = document.getElementById('confirmOverlay');
  if (!overlay) return;
  const titleEl = document.getElementById('confirmTitle');
  const messageEl = document.getElementById('confirmMessage');
  const cancelBtn = document.getElementById('confirmCancel');
  const acceptBtn = document.getElementById('confirmAccept');
  let pendingForm = null;

  function closeDialog() {
    overlay.classList.remove('open');
    pendingForm = null;
  }

  document.querySelectorAll('form.js-confirm-delete').forEach(form => {
    form.addEventListener('submit', event => {
      if (form.dataset.confirmed === 'true') return;
      event.preventDefault();
      pendingForm = form;
      titleEl.textContent = form.dataset.confirmTitle || 'Confirmar eliminação';
      messageEl.textContent = form.dataset.confirmMessage || 'Tem certeza que deseja eliminar esta viatura?';
      overlay.classList.add('open');
    });
  });

  cancelBtn.addEventListener('click', closeDialog);
  overlay.addEventListener('click', e => { if (e.target === overlay) closeDialog(); });
  acceptBtn.addEventListener('click', () => {
    if (pendingForm) {
      pendingForm.dataset.confirmed = 'true';
      pendingForm.submit();
    }
    closeDialog();
  });
})();
