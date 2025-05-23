document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupPostMenu();
  setupEditPostModal();
  setupDeleteModal();
});

function setupTabs() {
  const postsTab = document.getElementById("posts-tab");
  const infoTab = document.getElementById("info-tab");
  const postsContent = document.getElementById("posts-content");
  const infoContent = document.getElementById("info-content");

  postsTab.addEventListener("click", () => toggleTabs(postsTab, infoTab, postsContent, infoContent));
  infoTab.addEventListener("click", () => toggleTabs(infoTab, postsTab, infoContent, postsContent));
}

function toggleTabs(activeTab, inactiveTab, activeContent, inactiveContent) {
  activeTab.classList.add("active");
  inactiveTab.classList.remove("active");
  activeContent.classList.remove("hidden");
  inactiveContent.classList.add("hidden");
}

function setupPostMenu() {
  document.querySelectorAll(".menu-button").forEach(button => {
    button.addEventListener("click", e => {
      e.stopPropagation();
      const menu = button.nextElementSibling;
      menu.classList.toggle("show");

      const closeMenu = event => {
        if (!menu.contains(event.target)) {
          menu.classList.remove("show");
        }
      };
    });
  });
}

function setupEditPostModal() {
  const modal = document.getElementById("edit-post-modal");
  const editForm = document.getElementById("edit-post-form");
  const closeModalBtn = modal.querySelector(".close-button");
  const imagePreview = modal.querySelector(".post-image-preview");
  const imageElement = imagePreview.querySelector("img");
  const removeImageInput = document.getElementById("remove-image-input");
  const newImageInput = document.getElementById("new-image-input");

  setupEditButtons(editForm, modal, imagePreview, imageElement, removeImageInput, newImageInput);
  setupImageAddButton(newImageInput, imagePreview, imageElement, removeImageInput);
  setupRemoveImageButton(modal, imagePreview, imageElement, removeImageInput, newImageInput);
  closeModalBtn.addEventListener("click", () => closeModal(modal));
}

function setupEditButtons(editForm, modal, imagePreview, imageElement, removeImageInput, newImageInput) {
  document.querySelectorAll(".edit-post").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      const { postId, postTitle, postImage, editUrl } = link.dataset;

      editForm.action = link.dataset.editUrl || "";

      document.getElementById("edit-post-id").value = postId;
      editForm.querySelector("textarea[name='title']").value = postTitle || "";

      if (postImage) {
        imagePreview.classList.remove("hidden");
        imageElement.src = postImage;
        removeImageInput.value = "false";
      } else {
        resetModalImage(imagePreview, imageElement, removeImageInput, newImageInput);
      }

      modal.classList.add("show");
    });
  });
}

function setupImageAddButton(newImageInput, imagePreview, imageElement, removeImageInput) {
  document.getElementById("add-image-button")?.addEventListener("click", () => newImageInput.click());

  newImageInput.addEventListener("change", function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = e => {
      imagePreview.classList.remove("hidden");
      imageElement.src = e.target.result;
      removeImageInput.value = "false";
    };
    reader.readAsDataURL(file);
  });
}

function setupRemoveImageButton(modal, imagePreview, imageElement, removeImageInput, newImageInput) {
  modal.querySelector(".remove-image-button")?.addEventListener("click", () => {
    resetModalImage(imagePreview, imageElement, removeImageInput, newImageInput);
    removeImageInput.value = "true";
  });
}

function closeModal(modal) {
  modal.classList.remove("show");
}

function resetModalImage(imagePreview, imageElement, removeImageInput, newImageInput) {
  imagePreview.classList.add("hidden");
  if (imageElement) imageElement.src = "";
  if (removeImageInput) removeImageInput.value = "false";
  if (newImageInput) newImageInput.value = "";
}

function setupDeleteModal() {
  const deleteModal = document.getElementById("confirm-delete-modal");
  let deleteUrl = "";

  document.querySelectorAll(".delete-post").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      deleteUrl = link.dataset.deleteUrl || "";
      if (deleteModal) deleteModal.classList.add("show");
    });
  });

  document.getElementById("confirm-delete-no")?.addEventListener("click", () => {
    if (deleteModal) deleteModal.classList.remove("show");
  });

  document.getElementById("confirm-delete-yes")?.addEventListener("click", () => {
    if (deleteUrl) window.location.href = deleteUrl;
  });
}

function toggleComment(btn) {
  const commentBox = btn.closest(".post")?.querySelector(".comment-input");
  if (commentBox) {
    commentBox.style.display = commentBox.style.display === "none" ? "block" : "none";
  }
}

function toggleCommentList(btn) {
  const list = btn.closest(".post")?.querySelector(".comments-list");
  if (list) {
    list.style.display = list.style.display === "none" ? "block" : "none";
  }
}
