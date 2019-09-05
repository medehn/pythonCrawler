function newSearch(link) {
    let textfield = document.getElementById("inputUrl");

    if (link.includes("http")) {
        textfield.value = link;
        document.getElementById("searchButton").click();
    }
    else {
        textfield.value += link;
        document.getElementById("searchButton").click();
    }
}

