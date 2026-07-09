function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    input.type = input.type === "password" ? "text" : "password";
}

document.addEventListener("DOMContentLoaded", () => {
    const messageArea = document.getElementById("message-area");
    if (messageArea) {
        messageArea.scrollTop = messageArea.scrollHeight;
    }
});
