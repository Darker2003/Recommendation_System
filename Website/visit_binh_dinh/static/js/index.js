function turn_overlay_on(index) {
    let id_name = "locationoverlay" + index
    document.getElementById(id_name).style.display = "block";
}

function turn_overlay_off(index) {
    let id_name = "locationoverlay" + index
    document.getElementById(id_name).style.display = "none";
}