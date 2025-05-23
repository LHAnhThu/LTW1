function confirmDelete(id, title) {
  const modal = document.getElementById('delete-modal');
  const form = document.getElementById('delete-form');
  const titleSpan = document.getElementById('delete-title');

  if (!modal || !form || !titleSpan) return;

  form.action = `/admin_home/notifications/delete/${id}/`;
  titleSpan.textContent = title;
  modal.classList.add('show');
}

function closeModal() {
  document.getElementById('delete-modal')?.classList.remove('show');
}

function toggleDepartments() {
  const recipientType = document.querySelector('input[name="recipient_type"]:checked').value;
  const container = document.getElementById('departments-container');
  if (container) {
    container.style.display = recipientType === 'department' ? 'block' : 'none';
  }
}

document.querySelectorAll('input[name="recipient_type"]').forEach(radio => {
  radio.addEventListener('change', toggleDepartments);
});

window.addEventListener('DOMContentLoaded', toggleDepartments);

