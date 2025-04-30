$(function () {
  $("#add-root-assembly").click(function () {
    console.log("Root assembly button clicked");
    const $assembly = $($("#assembly-template").html());
    $("#assemblies-root").append($assembly);
  });

  $("#assemblies-root").on("click", ".add-sub-assembly", function () {
    const $subAssembly = $($("#assembly-template").html());
    $(this).parent().siblings(".sub-assemblies").first().append($subAssembly);
  });

  $("#assemblies-root").on("click", ".add-part", function () {
    const $part = $($("#part-template").html());
    $(this).parent().siblings(".parts").first().append($part);
  });
});

function buildTree($element) {
  const name = $element
    .children(".d-flex")
    .find('input[name="assembly_name"]')
    .val()
    .trim();
  if (!name) return null;

  const parts = $element
    .children(".parts")
    .children(".part")
    .map(function () {
      const partName = $(this).find('input[name="part_name"]').val().trim();
      return partName ? { name: partName } : null;
    })
    .get()
    .filter(Boolean);

  const subAssemblies = $element
    .children(".sub-assemblies")
    .children(".assembly")
    .map(function () {
      return buildTree($(this));
    })
    .get()
    .filter(Boolean);

  return { name, parts, sub_assemblies: subAssemblies };
}

function submitData() {
  const machineName = $("#machine-name").val().trim();
  const assemblies = $("#assemblies-root > .assembly")
    .map(function () {
      return buildTree($(this));
    })
    .get()
    .filter(Boolean);

  const payload = {
    name: machineName,
    assemblies: assemblies,
  };

  fetch(saveUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ machine: payload }),
  })
    .then((response) => response.json())
    .then((data) => alert("Saved successfully!"))
    .catch((error) => alert("Error saving: " + error));
}
