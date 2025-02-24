import "clsx";
import { T as pop, Q as push } from "../../../chunks/index.js";
import "../../../chunks/config.js";
import { L as Loading } from "../../../chunks/Loading.js";
function _page($$payload, $$props) {
  push();
  $$payload.out += `<div class="space-y-6"><div class="flex justify-between items-center"><h2 class="text-3xl font-bold text-gray-900 dark:text-white">Sustainability Reports</h2></div> `;
  {
    $$payload.out += "<!--[-->";
    Loading($$payload, { size: "lg" });
  }
  $$payload.out += `<!--]--></div>`;
  pop();
}
export {
  _page as default
};
