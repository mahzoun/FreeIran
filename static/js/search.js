(function () {
  const inputs = document.querySelectorAll("[data-autocomplete]");
  if (!inputs.length) return;

  const datalist = document.getElementById("search-suggestions");
  let timer;

  function updateSuggestions(query) {
    if (!query) {
      datalist.innerHTML = "";
      return;
    }
    fetch(`/api/v1/suggest/?q=${encodeURIComponent(query)}`)
      .then((response) => response.json())
      .then((data) => {
        datalist.innerHTML = "";
        (data.results || []).forEach((name) => {
          const option = document.createElement("option");
          option.value = name;
          datalist.appendChild(option);
        });
      })
      .catch(() => {
        datalist.innerHTML = "";
      });
  }

  inputs.forEach((input) => {
    input.addEventListener("input", function (event) {
      clearTimeout(timer);
      timer = setTimeout(() => updateSuggestions(event.target.value.trim()), 250);
    });
  });
})();
