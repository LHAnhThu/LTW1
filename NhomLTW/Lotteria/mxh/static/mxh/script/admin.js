document.addEventListener('DOMContentLoaded', () => {
  // Hiển thị tên file khi chọn ảnh
  const imageInput = document.getElementById('id_image_url') || document.getElementById('image');
  const fileNameDisplay = document.getElementById('file-name');

  if (imageInput && fileNameDisplay) {
    imageInput.addEventListener('change', () => {
      const fileName = imageInput.files[0]?.name || '';
      fileNameDisplay.textContent = fileName;
    });
  }

  // Hiển thị/ẩn phần chọn bộ phận theo radio recipient_type
  const recipientRadios = document.querySelectorAll('input[name="recipient_type"]');
  const departmentsContainer = document.getElementById('departments-container');

  function toggleDepartments() {
    const selected = document.querySelector('input[name="recipient_type"]:checked');
    if (departmentsContainer && selected) {
      departmentsContainer.style.display = selected.value === 'department' ? 'block' : 'none';
    }
  }

  recipientRadios.forEach(radio => radio.addEventListener('change', toggleDepartments));
  toggleDepartments();
});

// Xác nhận xóa thông báo
function confirmDelete(id, title) {
  const modal = document.getElementById('delete-modal');
  const form = document.getElementById('delete-form');
  const titleSpan = document.getElementById('delete-title');

  if (modal && form && titleSpan) {
    form.action = `/admin_home/notifications/delete/${id}/`;
    titleSpan.textContent = title;
    modal.classList.add('show');
  }
}

function closeModal() {
  const modal = document.getElementById('delete-modal');
  if (modal) modal.classList.remove('show');
}
