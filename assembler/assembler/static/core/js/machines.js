$(function () {
  $(".toggle-info").click(function () {
    const machineId = $(this).data("id");
    const detailsDiv = $("#machine-details-" + machineId);
    const icon = $(this).find("i");

    const collapse = new bootstrap.Collapse(detailsDiv[0], {
      toggle: false,
    });

    if (detailsDiv.hasClass("show")) {
      collapse.hide();
      icon.removeClass("bi-chevron-up").addClass("bi-chevron-down");
    } else {
      collapse.show();
      icon.removeClass("bi-chevron-down").addClass("bi-chevron-up");
    }
  });
});
