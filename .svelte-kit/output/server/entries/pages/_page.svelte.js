import "clsx";
import { T as pop, Q as push } from "../../chunks/index.js";
import { L as Loading } from "../../chunks/Loading.js";
function _page($$payload, $$props) {
  push();
  $$payload.out += `<div class="space-y-6"><h1 class="text-3xl font-bold mb-8">Sustainability Intelligence Dashboard</h1> `;
  {
    $$payload.out += "<!--[-->";
    $$payload.out += `<div class="loading svelte-1y8ymr">`;
    Loading($$payload, { size: "lg" });
    $$payload.out += `<!----></div>`;
  }
  $$payload.out += `<!--]--></div>`;
  pop();
}
export {
  _page as default
};
