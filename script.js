function toggleLanguage() {
    const englishContent = document.getElementById("english");
    const italianContent = document.getElementById("italian");

    const navBiography = document.getElementById("nav-biography");
    const navResearch = document.getElementById("nav-research");
    const navTutoring = document.getElementById("nav-tutoring");
    const navContact = document.getElementById("nav-contact");

    const englishIsVisible = englishContent.style.display !== "none";

    if (englishIsVisible) {

        // Show Italian content
        englishContent.style.display = "none";
        italianContent.style.display = "block";

        // Change navigation to Italian
        navBiography.textContent = "Biografia";
        navBiography.href = "#biografia";

        navResearch.textContent = "Ricerca";
        navResearch.href = "#ricerca";

        navTutoring.textContent = "Inglese & Colloqui";
        navTutoring.href = "#tutoraggio";

        navContact.textContent = "Contatti";
        navContact.href = "#contatti";

    } else {

        // Show English content
        englishContent.style.display = "block";
        italianContent.style.display = "none";

        // Change navigation to English
        navBiography.textContent = "Biography";
        navBiography.href = "#biography";

        navResearch.textContent = "Research";
        navResearch.href = "#research";

        navTutoring.textContent = "Tutoring";
        navTutoring.href = "#tutoring";

        navContact.textContent = "Contact";
        navContact.href = "#contact";
    }
}
