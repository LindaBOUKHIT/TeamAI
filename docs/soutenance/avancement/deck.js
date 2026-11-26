// Navigation du support J3 : flèches, espace ou clic pour avancer, F pour le plein écran.
// L'impression (Ctrl+P → Enregistrer au format PDF) affiche toutes les slides, une par page.
const slides = [...document.querySelectorAll(".slide")];
let current = Math.min(Math.max(Number(location.hash.slice(1)) - 1 || 0, 0), slides.length - 1);

function fit() {
  const scale = Math.min(innerWidth / 1920, innerHeight / 1080);
  document.documentElement.style.setProperty("--scale", scale);
}

function show(index) {
  current = Math.min(Math.max(index, 0), slides.length - 1);
  slides.forEach((slide, i) => slide.classList.toggle("active", i === current));
  history.replaceState(null, "", `#${current + 1}`);
}

addEventListener("resize", fit);
addEventListener("keydown", (event) => {
  if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) show(current + 1);
  else if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) show(current - 1);
  else if (event.key === "Home") show(0);
  else if (event.key === "End") show(slides.length - 1);
  else if (event.key.toLowerCase() === "f") document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();
});
addEventListener("click", (event) => show(current + (event.clientX < innerWidth / 3 ? -1 : 1)));

fit();
show(current);
