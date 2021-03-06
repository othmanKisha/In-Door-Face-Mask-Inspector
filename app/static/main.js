const toggleTheme = () => {
  const htmlTag = document.getElementsByTagName("html")[0];
  const navTag = document.getElementsByTagName("nav")[0];
  const cards = document.getElementsByClassName("card");
  const buttons = document.getElementsByClassName("card-btn");
  const tables = document.getElementsByClassName("card-tbl");
  const inputs = document.getElementsByClassName("card-inp");

  if (htmlTag.hasAttribute("theme")) {
    htmlTag.removeAttribute("theme");

    navTag.classList.remove("navbar-dark");
    navTag.classList.add("navbar-light");
    navTag.classList.remove("bg-dark");
    navTag.classList.add("bg-light");

    if (cards !== null)
      for (let i = 0; i < cards.length; i++) {
        cards[i].classList.remove("bg-dark");
        cards[i].classList.add("bg-light");
      }

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

  if (cards !== null)
    for (let i = 0; i < cards.length; i++) {
      cards[i].classList.remove("bg-light");
      cards[i].classList.add("bg-dark");
    }

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

$("#searchinpS").on("keyup", function () {
  let value = $(this)[0].value.toLowerCase();

  $("#tableBodyS tr").filter(function () {
    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
  });
});

$("#select-room").change(function () {
  let roomValue = $(this)[0].value.toLowerCase();
  let dateValue = $("#select-date")[0].value.toLowerCase();
  if (roomValue !== "all") {
    let room = `room: ${roomValue}`;
    if (dateValue !== "all") {
      let date = `date: ${dateValue}`;
      $(".filter-card").filter(function () {
        $(this).toggle(
          $(this).text().toLowerCase().indexOf(room) > -1 &&
            $(this).text().toLowerCase().indexOf(date) > -1
        );
      });
    } else {
      $(".filter-card").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(room) > -1);
      });
    }
  } else {
    if (dateValue !== "all") {
      let date = `date: ${dateValue}`;
      $(".filter-card").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(date) > -1);
      });
    } else
      $(".filter-card").filter(function () {
        $(this).toggle();
      });
  }
});

$("#select-date").change(function () {
  let dateValue = $(this)[0].value.toLowerCase();
  let roomValue = $("#select-room")[0].value.toLowerCase();
  if (dateValue !== "all") {
    let date = `date: ${dateValue}`;
    if (roomValue !== "all") {
      let room = `room: ${roomValue}`;
      $(".filter-card").filter(function () {
        $(this).toggle(
          $(this).text().toLowerCase().indexOf(date) > -1 &&
            $(this).text().toLowerCase().indexOf(room) > -1
        );
      });
    } else {
      $(".filter-card").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(date) > -1);
      });
    }
  } else {
    if (roomValue !== "all") {
      let room = `room: ${roomValue}`;
      $(".filter-card").filter(function () {
        $(this).toggle($(this).text().toLowerCase().indexOf(room) > -1);
      });
    } else
      $(".filter-card").filter(function () {
        $(this).toggle();
      });
  }
});
