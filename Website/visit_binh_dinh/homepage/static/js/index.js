function turn_overlay_on(index) {
    let id_name = "locationoverlay" + index
    document.getElementById(id_name).style.display = "block";
}

function turn_overlay_off(index) {
    let id_name = "locationoverlay" + index
    document.getElementById(id_name).style.display = "none";
}

function showMoreTags() {
const hiddenTags = document.querySelectorAll('.hidden-tag');
hiddenTags.forEach(tag => {
    tag.classList.remove('hidden-tag');
});
document.getElementById('show-more-button').style.display = 'none';
document.getElementById('show-less-button').style.display = 'block';
}

function showLessTags() {
const tags = document.querySelectorAll('.tag-btn');
tags.forEach((tag, index) => {
    if (index >= 5) {
    tag.classList.add('hidden-tag');
    }
});
document.getElementById('show-more-button').style.display = 'block';
document.getElementById('show-less-button').style.display = 'none';
}

window.addEventListener('scroll', function() {
    const section = document.getElementById('infosection');
    const position = section.getBoundingClientRect();

    if (position.top < window.innerHeight && position.bottom >= 0) {
        section.classList.add('show');
    }
});


const scrollTopBtn = document.getElementById("scrollTopBtn");

window.onscroll = function() {
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        scrollTopBtn.style.display = "block";
    } else {
        scrollTopBtn.style.display = "none";
    }
};

scrollTopBtn.addEventListener("click", function() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});