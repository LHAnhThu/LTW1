document.addEventListener("DOMContentLoaded", () => {
  const toggleTabs = (activeTab, inactiveTab, showContent, hideContent) => {
    activeTab.classList.add("active");
    inactiveTab.classList.remove("active");
    showContent.classList.remove("hidden");
    hideContent.classList.add("hidden");
  };

  const postsTab = document.getElementById("posts-tab");
  const infoTab = document.getElementById("info-tab");
  const postsContent = document.getElementById("posts-content");
  const infoContent = document.getElementById("info-content");

  postsTab.addEventListener("click", () => toggleTabs(postsTab, infoTab, postsContent, infoContent));
  infoTab.addEventListener("click", () => toggleTabs(infoTab, postsTab, infoContent, postsContent));

  document.querySelectorAll(".menu-button").forEach(btn => {
    btn.addEventListener("click", e => {
      e.stopPropagation();
      document.querySelectorAll(".dropdown-menu").forEach(menu => menu.classList.remove("show"));
      btn.nextElementSibling.classList.toggle("show");
    });
  });

  document.addEventListener("click", () => {
    document.querySelectorAll(".dropdown-menu").forEach(menu => menu.classList.remove("show"));
  });

  const editModal = document.getElementById("edit-post-modal");
  const textarea = editModal.querySelector(".post-textarea");
  const imagePreview = editModal.querySelector(".post-image-preview");
  const imageElement = imagePreview.querySelector("img");
  const postIdInput = editModal.querySelector("#edit-post-id");
  const avatarUrlInput = editModal.querySelector("#edit-post-image");
  const removeImageInput = editModal.querySelector("#remove-image-input");

  document.querySelectorAll(".edit-post").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      postIdInput.value = link.dataset.postId;
      textarea.value = link.dataset.postTitle || "";

      if (link.dataset.postImage) {
        avatarUrlInput.value = link.dataset.postImage;
        imageElement.src = link.dataset.postImage;
        imagePreview.classList.remove("hidden");
      } else {
        imagePreview.classList.add("hidden");
      }

      editModal.querySelector("form").action = link.href;
      editModal.classList.add("show");
    });
  });

  editModal.querySelector(".close-button").addEventListener("click", () => {
    editModal.classList.remove("show");
  });

  editModal.querySelector(".remove-image-button").addEventListener("click", () => {
    imagePreview.classList.add("hidden");
    removeImageInput.value = "true";
    avatarUrlInput.value = "";
  });

  document.getElementById("add-image-button").addEventListener("click", () => {
    document.getElementById("new-image-input").click();
  });

  const confirmModal = document.getElementById("confirm-delete-modal");
  let deleteUrl = "";
  document.querySelectorAll(".delete-post").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      deleteUrl = btn.dataset.deleteUrl;
      confirmModal.classList.add("show");
    });
  });

  document.getElementById("confirm-delete-yes").addEventListener("click", () => {
    window.location.href = deleteUrl;
  });

  document.getElementById("confirm-delete-no").addEventListener("click", () => {
    confirmModal.classList.remove("show");
  });
});
