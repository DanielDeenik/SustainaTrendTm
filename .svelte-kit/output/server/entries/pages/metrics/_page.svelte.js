import { Z as ensure_array_like, a4 as attr, a7 as escape_html, T as pop, Q as push, a5 as stringify } from "../../../chunks/index.js";
import "../../../chunks/config.js";
import { L as Loading } from "../../../chunks/Loading.js";
function _page($$payload, $$props) {
  push();
  let selectedCategory = null;
  const categories = [
    "emissions",
    "water",
    "energy",
    "waste",
    "social",
    "governance"
  ];
  const each_array = ensure_array_like(categories);
  $$payload.out += `<div class="space-y-6"><div class="flex justify-between items-center"><h2 class="text-3xl font-bold text-gray-900 dark:text-white">Sustainability Metrics</h2> <div class="flex gap-2"><button${attr("class", `px-4 py-2 rounded-lg ${stringify("bg-primary text-white")}`)}>All</button> <!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let category = each_array[$$index];
    $$payload.out += `<button${attr("class", `px-4 py-2 rounded-lg ${stringify(selectedCategory === category ? "bg-primary text-white" : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300")}`)}>${escape_html(category)}</button>`;
  }
  $$payload.out += `<!--]--></div></div> `;
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
