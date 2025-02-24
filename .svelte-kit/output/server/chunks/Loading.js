import { a4 as attr, a2 as bind_props, Y as fallback, a5 as stringify } from "./index.js";
function Loading($$payload, $$props) {
  let size = fallback($$props["size"], "md");
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12"
  };
  $$payload.out += `<div class="loading"><div${attr("class", `spinner ${stringify(sizeClasses[size])}`)}></div></div>`;
  bind_props($$props, { size });
}
export {
  Loading as L
};
