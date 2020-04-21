var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
    });
}

function num_colonnes(btn) {
    var liste = document.querySelectorAll("[class^=wrapper]")
    num = 12 / btn.value
    for (var elt of liste) {
        elt.classList = "wrapper col-" + num;
    }
}

function show_infos(btn) {
    var liste = document.querySelectorAll("[class^=" + btn.value)
    for (var elt of liste) {
        if (elt.style.display === "none") {
            elt.style.display = "block";
            btn.classList = "btn btn-info"
        } else {
            elt.style.display = "none";
            btn.classList = "btn btn-outline-info"
        }
    }
}