document.addEventListener("DOMContentLoaded", function () {
    const editBtn = document.getElementById("editProfileBtn");
    const modal = document.getElementById("editProfileModal");
    const closeBtn = document.querySelector(".modal .close");

    if (editBtn && modal && closeBtn) {
        editBtn.onclick = function () {
            modal.style.display = "block";
        };

        closeBtn.onclick = function () {
            modal.style.display = "none";
        };

        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    }
});
