function toggleLanguage() {
    let englishContent = document.getElementById("english");
    let italianContent = document.getElementById("italian");

    if (englishContent.style.display === "none") {
        englishContent.style.display = "block";
        italianContent.style.display = "none";
    } else {
        englishContent.style.display = "none";
        italianContent.style.display = "block";
    }
}
