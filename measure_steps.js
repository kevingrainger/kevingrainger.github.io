// measure_steps.js: paste into the browser console on the built page (desktop width, ~1366 px).
// Opens one project's timeline and reports, for every step, how far the text runs against
// the figure column, so figures can be added where the text runs on past them.
//   room > 0   : spare height under the figures (px) that another figure could fill
//   room < 0   : the figures already run past the text
// Usage: measureSteps("dft-porphyrin-networks")  (any part of the project's folder name)
async function measureSteps(folder) {
  const li = [...document.querySelectorAll("li.project")].find(l => l.innerHTML.includes(folder + "/"));
  if (!li.classList.contains("open")) li.querySelector(".project-head").click();
  await new Promise(r => setTimeout(r, 500));
  const vm = li.querySelector(".view-more");
  if (vm && vm.getAttribute("aria-expanded") !== "true") vm.click();
  await new Promise(r => setTimeout(r, 800));
  const imgs = [...li.querySelectorAll(".step img")];
  imgs.forEach(i => (i.loading = "eager"));
  await Promise.all(imgs.map(i => (i.complete && i.naturalHeight ? 1 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 8000); }))));
  return [...li.querySelectorAll(".step")].map(s => {
    const kids = [...s.querySelector("div").children];
    const text = kids[kids.length - 1].getBoundingClientRect().bottom - kids[0].getBoundingClientRect().top;
    const figs = [...s.querySelectorAll("figure")];
    const col = figs[figs.length - 1].getBoundingClientRect().bottom - figs[0].getBoundingClientRect().top;
    return { step: s.querySelector("h5").innerText.replace(/\n/g, " "), text: Math.round(text), figures: figs.length,
             figureColumn: Math.round(col), room: Math.round(text - col) };
  });
}
