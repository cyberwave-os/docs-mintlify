document.addEventListener("click", async (event) => {
  const button = event.target.closest?.("button[data-agent-prompt]");
  if (!button) return;
  const status = button.parentElement.querySelector("[data-agent-prompt-status]");
  try {
    await navigator.clipboard.writeText(button.dataset.agentPrompt);
    button.textContent = "Copied!";
    status.textContent = "Agent prompt copied to clipboard.";
    status.className = "sr-only";
  } catch {
    status.textContent = "Copy failed. Allow clipboard access in your browser and try again.";
    status.className = "block mt-2 text-sm";
  }
});
