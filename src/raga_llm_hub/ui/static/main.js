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

document.addEventListener("DOMContentLoaded", init);
function init() {
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
  setupNavigation();
}
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
  } else {
    uncheckHandler(input);
  }
  getCheckedValues();
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
  enableClientSideNavigation();
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

function setupNavigation() {
  enableClientSideNavigation();
  localStorage.setItem("id", location.search);
  navigation.addEventListener("navigate", (event) => {
    const targetUrl = event.destination.url;
    if (targetUrl.includes("/trace/")) {
      const traceId = targetUrl.split("/").pop();
      renderTraceDetailView(traceId);
    } else {
      renderIndexPage();
    }
    // URL changed!
  });
  window.onbeforeunload = function () {
    return true;
  };
}

function renderTraceDetailView(traceId) {
  const traceObj = jsonData.find((e) => e.data_point_id === traceId);
  if (traceObj) {
    const html = generateTracePageHtml(traceObj);
    paintBody(html);
    wireClickEvents();
    window.gtag("event", "trace_view_loaded");
  }
}

function wireClickEvents() {
  const backBtn = document.querySelector(".back-btn");
  backBtn.addEventListener("click", () => {
    history.replaceState(
      null,
      null,
      `/${localStorage.getItem("id", location.search)}`
    );
  });
}

function renderIndexPage() {
  const bodyEl = document.getElementsByTagName("body")[0];
  bodyEl.querySelector("div#trace-page")?.remove();
  bodyEl.querySelector("div#index-page").style = "display: block";
  document.querySelectorAll("div[id*=card-]").forEach((e) => (e.style = ""));
  addEventHandlerOnCheckbox();
  getCheckedValues();
  showToolTip();
  enableClientSideNavigation();
}

function paintBody(html) {
  const bodyEl = document.getElementsByTagName("body")[0];
  bodyEl.querySelector("div#index-page").style = "display: none";
  bodyEl.querySelector("div#trace-page")?.remove();
  bodyEl.innerHTML = bodyEl.innerHTML + html;
}

function enableClientSideNavigation() {
  const links = document.querySelectorAll("a");
  links.forEach((link) => {
    link.addEventListener("click", gotoTraceViewPageHandler);
  });
}

function gotoTraceViewPageHandler(event) {
  event.preventDefault();
  const link = event.target;
  const target = link.getAttribute("href");
  history.pushState(null, null, target);
  link.removeEventListener("click", gotoTraceViewPageHandler);
}

function generateTracePageHtml(result) {
  const tests = result.dynamic;
  const testsHtml = tests
    .map((test) => {
      return `
    <div class="card-badge">
      <div class="listItem">
        <span>${test.test_name}</span><span>${test.score}</span>
      </div>
    </div>
    `;
    })
    .join("");

  return `
<div id="trace-page" class="container-fluid p-5 min-vh-100">
  <div class="row">
    <div class="col-12">
      <a class="back-btn">
        <i class="bi bi-chevron-left"></i> Go Back
      </a>
      <h1 class="mb-0 mt-2">Trace Details</h1>
    </div>
  </div>
  <div class="row mt-2">
    <div class="col-12">
      <div class="raga-card">
        <div class="p-3">
          <div class="row">
            <div class="col-auto" style="min-width: 9.375rem">
              <p class="mb-0 mt-1">Id</p>
            </div>
            <div class="col">${result.data_point_id || "--"}</div>
          </div>
          <div class="row">
            <div class="col-auto" style="min-width: 9.375rem">
              <p class="mb-0 mt-1">Metrics</p>
            </div>
            <div class="col">
              ${testsHtml}
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- SideBar -->
    <div class="col-lg-3">
      <div class="raga-card shadow card-hover my-3">
        <div id="accordian">
          <ul class="show-dropdown">
            <li>
              <a href="javascript:void(0);">
                Generation
                <span class="badge-red">TRACE</span>
              </a>
              <ul>
                <li><a href="javascript:void(0);">1</a></li>
                <li><a href="javascript:void(0);">1</a></li>
                <li><a href="javascript:void(0);">1</a></li>
                <li><a href="javascript:void(0);">1</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </div>
    <!-- Dynamic View -->
    <div class="col-lg-9">
      <div class="raga-card shadow card-hover my-3">
        <div class="raga-card-header">
          <div class="raga-card-header-first">
            <h4 class="mb-0">
              Generation <span class="badge-red">TRACE</span>
            </h4>
          </div>
        </div>
        <div class="raga-card-body p-3">
          ${section("Prompt", result.prompt || result.input)}
          ${section("Response", result.response, "bg-light-green")}
          ${
            result.expected_response
              ? section("Ground Truth", result.expected_response)
              : ""
          }
          ${result.context ? section("Context", result.context) : ""}
        </div>
      </div>
    </div>
  </div>
</div>
  `;
}

function section(header, p, classNames = "bg-body") {
  if (p && typeof p === "object") {
    p = JSON.stringify(p, null, 2);
  } else if (typeof p !== "string") {
    p = "--";
  }

  return `
    <div class="mb-4">
      <h6>${header}</h6>

      <div class="${classNames} p-3">
        <p>${p}</p>
      </div>
    </div>
  `;
}
