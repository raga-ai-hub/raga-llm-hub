function sorting(arr, sortBy, sortDir) {
  return arr.sort((a, b) => {
    const itemA = a.dynamic.find((e) => e.test_run_id === sortBy)?.score;
    const itemB = b.dynamic.find((e) => e.test_run_id === sortBy)?.score;
    if (typeof itemA === "string") {
      return sortDir === "asc"
        ? itemA.localeCompare(itemB)
        : itemB.localeCompare(itemA);
    }
    return sortDir === "asc" ? itemA - itemB : itemB - itemA;
  });
}

function tableDataMapper(arr, activeTests, sortBy, sortDir) {
  let result = arr.map((e) => ({
    ...e,
    dynamic: e.dynamic.filter((d) => activeTests.includes(d.test_run_id)),
  }));

  if (
    sortBy === undefined ||
    sortDir === undefined ||
    !activeTests.includes(sortBy)
  ) {
    return result;
  }

  const dataToBeSorted = result.filter((e) =>
    e.dynamic.find((d) => d.test_run_id === sortBy)
  );
  const dataNotToBeSorted = result.filter((e) => !dataToBeSorted.includes(e));
  if (sortDir === "asc") {
    return [...sorting(dataToBeSorted, sortBy, sortDir), ...dataNotToBeSorted];
  }
  return [...dataNotToBeSorted, ...sorting(dataToBeSorted, sortBy, sortDir)];
}

// -------multilevel-accordian-menu---------
function setupAccordian() {
  $("#accordian a").click(function () {
    var link = $(this);
    var closest_ul = link.closest("ul");
    var parallel_active_links = closest_ul.find(".active");
    var closest_li = link.closest("li");
    var link_status = closest_li?.hasClass("active");
    var count = 0;

    closest_ul.find("ul").slideUp(function () {
      if (++count == closest_ul.find("ul").length) {
        parallel_active_links.removeClass("active");
        parallel_active_links.children("ul").removeClass("show-dropdown");
      }
    });

    if (!link_status) {
      closest_li.children("ul").slideDown().addClass("show-dropdown");
      closest_li
        .parent()
        .parent("li.active")
        .find("ul")
        .find("li.active")
        .removeClass("active");
      link.parent().addClass("active");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  // setupAccordian();
  // Get current path and find target link
  var path = window.location.pathname.split("/").pop();

  // Account for home page with empty path
  if (path == "") {
    path = "index.html";
  }

  var target = $('#accordian li a[href="' + path + '"]');
  // Add active class to target link
  target.parents("li").addClass("active");
  target.parents("ul").addClass("show-dropdown");

  addEventHandlerOnCheckbox();
  getCheckedValues();
  showToolTip();
});
// --------for-active-class-on-other-page-----------

function addEventHandlerOnCheckbox() {
  const target = document.querySelectorAll(
    'input[type="checkbox"].form-check-input'
  );

  for (const t of target) {
    t.addEventListener("click", checkboxEventHandler);
  }
}

function checkboxEventHandler(event) {
  const input = event.target;
  if (input.checked) {
    checkHandler(input);
    getCheckedValues();
  } else {
    uncheckHandler(input);
    getCheckedValues();
  }
}

function uncheckHandler(input) {
  const testName = input.dataset.target;
  $(`div#card-${testName}.raga-card`).hide();
}

function checkHandler(input) {
  const testName = input.dataset.target;
  $(`div#card-${testName}.raga-card`).show();
}

function getTestNameForTestRunId(testRunId) {
  for (let e of jsonData) {
    for (let d of e.dynamic) {
      if (d.test_run_id === testRunId) {
        return d.test_name;
      }
    }
  }
}
//create a table using javascript
function populateTableHead(headings) {
  //   var elementToRemove = document.querySelector(".p-table.clone");
  //   elementToRemove?.remove();

  var thead = document.querySelector("#table-scroll thead");
  thead.innerHTML = "";

  var rowHead = document.createElement("tr");
  headings.forEach(function (head) {
    var headCell = document.createElement("th");
    if (
      head == "Id" ||
      head == "Trace" ||
      head == "prompt" ||
      head == "response"
    ) {
      headCell.textContent = head;
      headCell.classList.add("fixed-side");
    } else {
      headCell.addEventListener("click", function () {
        let sortValue = this.getAttribute("data-sortValue");
        var sortIcon = this.querySelector(".sort-icon");

        if (sortValue == "asc") {
          sortIcon.classList.remove("bi-sort-up");
          sortIcon.classList.add("bi-sort-down");
          headCell.setAttribute("data-sortValue", "desc");
          sortValue = "desc";
        } else {
          sortIcon.classList.add("bi-sort-up");
          sortIcon.classList.remove("bi-sort-down");
          headCell.setAttribute("data-sortValue", "asc");
          sortValue = "asc";
        }
        onSort(head, sortValue);
      });
      headCell.innerHTML = `
            <span class='with-sort'>
                <span>${getTestNameForTestRunId(head)}</span>
                 <i class='sort-icon text-primary bi bi-sort-down'>  </i>
            </span>
            `;
    }
    // Append cells to the row
    rowHead.appendChild(headCell);
  });
  thead.appendChild(rowHead);

  //   jQuery(".p-table").clone(true).appendTo("#table-scroll").addClass("clone");
}

function populateTableBody(data, headings) {
  //   var elementToRemove = document.querySelector(".p-table.clone");
  //   elementToRemove?.remove();

  var tbody = document.querySelector("#table-scroll tbody");
  tbody.innerHTML = "";

  // Loop through data and create rows
  var Index = 1;
  data.forEach(function (item) {
    var row = document.createElement("tr");
    headings.forEach(function (head) {
      var bodyCell = document.createElement("td");
      if (head == "Trace") {
        bodyCell.innerHTML =
          "<a class='table-button' href='/trace/" +
          item?.data_point_id +
          "' > View <i class='bi bi-chevron-right'></i></a>";
      } else if (head == "Id") {
        bodyCell.textContent = Index;
      } else {
        const displayItem = item?.dynamic?.find((d) => d.test_run_id === head);
        if (displayItem) {
          bodyCell.textContent = displayItem?.score ?? "--";
          if (displayItem?.is_passed === true) {
            bodyCell.classList.add("text-success");
          } else {
            bodyCell.classList.add("text-danger");
          }
        } else {
          bodyCell.textContent = item?.[head] ? item?.[head] : "--";
        }
      }

      if (
        head == "Id" ||
        head == "Trace" ||
        head == "prompt" ||
        head == "response"
      ) {
        bodyCell.classList.add("fixed-side");
      }

      // Append cells to the row
      row.appendChild(bodyCell);
    });
    Index++;
    // Append row to the tbody
    tbody.appendChild(row);
  });
}

function getTableLeftValue() {
  const table = document.querySelector("#table-scroll table");
  const ths = table.querySelectorAll("thead .fixed-side");

  var widths = [];
  ths.forEach((th) => {
    widths.push(th.offsetWidth);
  });

  const leftValues = [];
  let left = 0;

  widths.forEach((width, index) => {
    if (index >= 0) {
      left += parseFloat(width);
      leftValues.push(`${left}px`);
    }
  });

  document.documentElement.style.setProperty("--left-1", leftValues[0]);
  document.documentElement.style.setProperty("--left-2", leftValues[1]);
  document.documentElement.style.setProperty("--left-3", leftValues[2]);
}

function populateTable(data, headings) {
  populateTableHead(headings);
  populateTableBody(data, headings);
  getTableLeftValue();
}

function getCheckedValues() {
  var checkboxes = document.querySelectorAll(".form-check-input:checked");
  var values = [];
  checkboxes.forEach(function (checkbox) {
    values.push(checkbox.dataset.target);
  });

  var data = tableDataMapper(jsonData, values);
  var headings = ["Id", "Trace", "prompt", "response", ...values];

  populateTable(data, headings);

  return values;
}

function onSort(key, sortValue) {
  var checkboxes = document.querySelectorAll(".form-check-input:checked");
  var values = [];
  checkboxes.forEach(function (checkbox) {
    values.push(checkbox.dataset.target);
  });

  var data = tableDataMapper(jsonData, values, key, sortValue);
  var headings = ["Id", "Trace", "prompt", "response", ...values];
  populateTableBody(data, headings);
}

function showToolTip() {
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}
