function turn_overlay_on(index) {
    let id_name = "locationoverlay" + index
    document.getElementById(id_name).style.display = "block";
}

function turn_overlay_off(index) {
    let id_name = "locationoverlay" + index
    document.getElementById(id_name).style.display = "none";
}

document.addEventListener("DOMContentLoaded", function() {
    var tagSearchInput = document.getElementById("tagSearch");
    var tags = document.getElementsByClassName("tag");

    tagSearchInput.addEventListener("input", function() {
        var searchTerm = tagSearchInput.value.trim().toLowerCase();

        for (var i = 0; i < tags.length; i++) {
            var tag = tags[i];
            var tagText = tag.textContent.trim().toLowerCase();
            
            if (tagText.includes(searchTerm)) {
                tag.style.display = "block";
            } else {
                tag.style.display = "none";
            }
        }
    });
});