(function () {
  var widget = document.querySelector(".toc-widget");
  if (!widget) return;
  var fab = widget.querySelector(".toc-fab");
  function setOpen(open) {
    widget.classList.toggle("open", open);
    fab.setAttribute("aria-expanded", String(open));
  }
  fab.addEventListener("click", function () {
    setOpen(!widget.classList.contains("open"));
  });
  widget.querySelectorAll(".toc-panel a").forEach(function (a) {
    a.addEventListener("click", function () { setOpen(false); });
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();
