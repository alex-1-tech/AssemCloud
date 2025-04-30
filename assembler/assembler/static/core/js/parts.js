document.addEventListener("DOMContentLoaded", function () {
  const csrfToken = "{{ csrf_token }}";
  document.querySelectorAll(".delete-part").forEach((button) => {
    button.addEventListener("click", function () {
      const partId = this.getAttribute("data-id");

      if (!confirm("Вы уверены, что хотите удалить эту деталь?")) return;

      fetch(`/parts/delete/${partId}/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "X-Requested-With": "XMLHttpRequest",
        },
      })
        .then((response) => {
          if (response.ok) {
            const partElement = document.getElementById(`part-${partId}`);
            if (partElement) {
              partElement.remove();
            }
          } else {
            alert("Ошибка при удалении детали.");
          }
        })
        .catch(() => {
          alert("Ошибка соединения с сервером.");
        });
    });
  });
});
