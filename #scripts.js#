document.addEventListener("DOMContentLoaded", function () {
    fetchLGA();

    document.getElementById("lga")?.addEventListener("change", function () {
        fetchWards(this.value);
    });

    document.getElementById("ward")?.addEventListener("change", function () {
        fetchPollingUnits(this.value);
    });
});

function fetchLGA() {
    fetch("/25/lga")
        .then(response => response.json())
        .then(data => populateDropdown("lga", data, "lga_id", "lga_name"));
}

function fetchWards(lgaId) {
    fetch(`/25/${lgaId}/wards`)
        .then(response => response.json())
        .then(data => populateDropdown("ward", data, "ward_id", "ward_name"));
}

function fetchPollingUnits(wardId) {
    fetch(`/25/25/${wardId}/pu`)
        .then(response => response.json())
        .then(data => populateDropdown("pu", data, "polling_unit_id", "polling_unit_name"));
}

function populateDropdown(elementId, data, valueKey, textKey) {
    let select = document.getElementById(elementId);
    select.innerHTML = '<option value="">Select</option>';
    data.forEach(item => {
        let option = document.createElement("option");
        option.value = item[valueKey];
        option.textContent = item[textKey];
        select.appendChild(option);
    });
}

function getResults() {
    let puId = document.getElementById("pu").value;
    let lgaId = document.getElementById("lga").value;

    let endpoint = puId ? `/${puId}` : `/${lgaId}/results`;

    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            document.getElementById("results").innerHTML = JSON.stringify(data, null, 2);
        });
}

function submitResults() {
    let data = {
        pu_uid: document.getElementById("pu").value,
        party_abbr: document.getElementById("party").value,
        party_score: document.getElementById("score").value,
        user: document.getElementById("user").value
    };

    fetch("/add_pu_result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    }).then(response => response.json())
      .then(result => alert(result.message));
}