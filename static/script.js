function moveInputToBottom() {
    // Add the "moved" class to the body when the form is submitted
    document.body.classList.add("moved");

    // Activate the output area if it's hidden
    const outputArea = document.getElementById("output_area");
    if (outputArea && !outputArea.classList.contains("active")) {
        outputArea.classList.add("active");
    }
}
