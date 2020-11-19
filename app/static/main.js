const toggleTheme = () => {
  const htmlTag = document.getElementsByTagName("html")[0];
  const navTag = document.getElementsByTagName("nav")[0];
  const cardTag = document.getElementsByClassName("card")[0];
  const buttons = document.getElementsByClassName("card-btn");
  const tables = document.getElementsByClassName("card-tbl");
  const inputs = document.getElementsByClassName("card-inp");

  if (htmlTag.hasAttribute("theme")) {
    htmlTag.removeAttribute("theme");

    navTag.classList.remove("navbar-dark");
    navTag.classList.add("navbar-light");
    navTag.classList.remove("bg-dark");
    navTag.classList.add("bg-light");

    cardTag.classList.remove("bg-dark");
    cardTag.classList.add("bg-light");

    if (buttons !== null)
      for (let i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove("btn-dark");
        buttons[i].classList.add("btn-light");
      }

    if (tables !== null)
      for (let i = 0; i < tables.length; i++) {
        tables[i].classList.remove("table-dark");
        tables[i].classList.add("table-light");
      }

    if (inputs !== null)
      for (let i = 0; i < inputs.length; i++) {
        inputs[i].classList.remove("bg-dark");
        inputs[i].classList.remove("text-light");
        inputs[i].classList.add("bg-light");
        inputs[i].classList.add("text-dark");
      }

    return window.localStorage.removeItem("site-theme");
  }

  htmlTag.setAttribute("theme", "dark");

  navTag.classList.remove("navbar-light");
  navTag.classList.add("navbar-dark");
  navTag.classList.remove("bg-light");
  navTag.classList.add("bg-dark");

  cardTag.classList.remove("bg-light");
  cardTag.classList.add("bg-dark");

  if (buttons !== null)
    for (let i = 0; i < buttons.length; i++) {
      buttons[i].classList.remove("btn-light");
      buttons[i].classList.add("btn-dark");
    }

  if (tables !== null)
    for (let i = 0; i < tables.length; i++) {
      tables[i].classList.remove("table-light");
      tables[i].classList.add("table-dark");
    }

  if (inputs !== null)
    for (let i = 0; i < inputs.length; i++) {
      inputs[i].classList.remove("bg-light");
      inputs[i].classList.remove("text-dark");
      inputs[i].classList.add("bg-dark");
      inputs[i].classList.add("text-light");
    }

  window.localStorage.setItem("site-theme", "dark");
};

const applyInitialTheme = () => {
  const theme = window.localStorage.getItem("site-theme");
  if (theme !== null) {
    if (theme === "dark") toggleTheme();
    const htmlTag = document.getElementsByTagName("html")[0];
    htmlTag.setAttribute("theme", theme);
  }
};

applyInitialTheme();

$("#theme-toggle").on("click", toggleTheme);

$("#searchinp").on("keyup", function () {
  let value = $(this)[0].value.toLowerCase();
  
  $("#tableBody tr").filter(function () {
    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
  });
});
