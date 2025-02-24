import { B as BROWSER, V as getContext, W as sanitize_props, X as rest_props, Q as push, Y as fallback, Z as ensure_array_like, _ as spread_attributes, $ as clsx, a0 as element, a1 as slot, a2 as bind_props, T as pop, a3 as spread_props, a4 as attr, a5 as stringify, a6 as store_get, a7 as escape_html, a8 as unsubscribe_stores } from "../../chunks/index.js";
import "../../chunks/client.js";
const dev = BROWSER;
const getStores = () => {
  const stores$1 = getContext("__svelte__");
  return {
    /** @type {typeof page} */
    page: {
      subscribe: stores$1.page.subscribe
    },
    /** @type {typeof navigating} */
    navigating: {
      subscribe: stores$1.navigating.subscribe
    },
    /** @type {typeof updated} */
    updated: stores$1.updated
  };
};
const page = {
  subscribe(fn) {
    const store = getStores().page;
    return store.subscribe(fn);
  }
};
/**
 * @license lucide-svelte v0.475.0 - ISC
 *
 * ISC License
 * 
 * Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 * ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 * ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 * OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 * 
 */
const defaultAttributes = {
  xmlns: "http://www.w3.org/2000/svg",
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  "stroke-width": 2,
  "stroke-linecap": "round",
  "stroke-linejoin": "round"
};
function Icon($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const $$restProps = rest_props($$sanitized_props, [
    "name",
    "color",
    "size",
    "strokeWidth",
    "absoluteStrokeWidth",
    "iconNode"
  ]);
  push();
  let name = fallback($$props["name"], void 0);
  let color = fallback($$props["color"], "currentColor");
  let size = fallback($$props["size"], 24);
  let strokeWidth = fallback($$props["strokeWidth"], 2);
  let absoluteStrokeWidth = fallback($$props["absoluteStrokeWidth"], false);
  let iconNode = fallback($$props["iconNode"], () => [], true);
  const mergeClasses = (...classes) => classes.filter((className, index, array) => {
    return Boolean(className) && array.indexOf(className) === index;
  }).join(" ");
  const each_array = ensure_array_like(iconNode);
  $$payload.out += `<svg${spread_attributes(
    {
      ...defaultAttributes,
      ...$$restProps,
      width: size,
      height: size,
      stroke: color,
      "stroke-width": absoluteStrokeWidth ? Number(strokeWidth) * 24 / Number(size) : strokeWidth,
      class: clsx(mergeClasses("lucide-icon", "lucide", name ? `lucide-${name}` : "", $$sanitized_props.class))
    },
    null,
    void 0,
    void 0,
    3
  )}><!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let [tag, attrs] = each_array[$$index];
    element($$payload, tag, () => {
      $$payload.out += `${spread_attributes({ ...attrs }, null, void 0, void 0, 3)}`;
    });
  }
  $$payload.out += `<!--]--><!---->`;
  slot($$payload, $$props, "default", {});
  $$payload.out += `<!----></svg>`;
  bind_props($$props, {
    name,
    color,
    size,
    strokeWidth,
    absoluteStrokeWidth,
    iconNode
  });
  pop();
}
function Activity($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"
      }
    ]
  ];
  Icon($$payload, spread_props([
    { name: "activity" },
    $$sanitized_props,
    {
      iconNode,
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {});
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
}
function Chart_column($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    ["path", { "d": "M3 3v16a2 2 0 0 0 2 2h16" }],
    ["path", { "d": "M18 17V9" }],
    ["path", { "d": "M13 17V5" }],
    ["path", { "d": "M8 17v-3" }]
  ];
  Icon($$payload, spread_props([
    { name: "chart-column" },
    $$sanitized_props,
    {
      iconNode,
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {});
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
}
function File_text($$payload, $$props) {
  const $$sanitized_props = sanitize_props($$props);
  const iconNode = [
    [
      "path",
      {
        "d": "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"
      }
    ],
    ["path", { "d": "M14 2v4a2 2 0 0 0 2 2h4" }],
    ["path", { "d": "M10 9H8" }],
    ["path", { "d": "M16 13H8" }],
    ["path", { "d": "M16 17H8" }]
  ];
  Icon($$payload, spread_props([
    { name: "file-text" },
    $$sanitized_props,
    {
      iconNode,
      children: ($$payload2) => {
        $$payload2.out += `<!---->`;
        slot($$payload2, $$props, "default", {});
        $$payload2.out += `<!---->`;
      },
      $$slots: { default: true }
    }
  ]));
}
function Navigation($$payload, $$props) {
  push();
  var $$store_subs;
  const routes = [
    {
      href: "/",
      label: "Dashboard",
      icon: Activity
    },
    {
      href: "/metrics",
      label: "Metrics",
      icon: Chart_column
    },
    {
      href: "/reports",
      label: "Reports",
      icon: File_text
    }
  ];
  const each_array = ensure_array_like(routes);
  const each_array_1 = ensure_array_like(routes);
  $$payload.out += `<nav class="nav"><div class="container"><div class="nav-content"><div class="flex"><div class="nav-brand"><span>Sustainability Intelligence</span></div> <div class="nav-links svelte-l0sn4m"><!--[-->`;
  for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
    let route = each_array[$$index];
    $$payload.out += `<a${attr("href", route.href)}${attr("class", `nav-link ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname === route.href ? "active" : "")}`)}><!---->`;
    route.icon?.($$payload, { class: "w-4 h-4" });
    $$payload.out += `<!----> ${escape_html(route.label)}</a>`;
  }
  $$payload.out += `<!--]--></div></div></div></div> <div class="nav-mobile svelte-l0sn4m"><div class="nav-mobile-content svelte-l0sn4m"><!--[-->`;
  for (let $$index_1 = 0, $$length = each_array_1.length; $$index_1 < $$length; $$index_1++) {
    let route = each_array_1[$$index_1];
    $$payload.out += `<a${attr("href", route.href)}${attr("class", `nav-link ${stringify(store_get($$store_subs ??= {}, "$page", page).url.pathname === route.href ? "active" : "")}`)}><!---->`;
    route.icon?.($$payload, { class: "w-5 h-5" });
    $$payload.out += `<!----> ${escape_html(route.label)}</a>`;
  }
  $$payload.out += `<!--]--></div></div></nav>`;
  if ($$store_subs) unsubscribe_stores($$store_subs);
  pop();
}
class Logger {
  logLevel = process.env.NODE_ENV === "development" ? "debug" : "info";
  formatError(error) {
    return {
      name: error.name,
      message: error.message,
      stack: process.env.NODE_ENV === "development" ? error.stack : void 0,
      ...error instanceof Error && "data" in error ? { data: error.data } : {}
    };
  }
  shouldLog(level) {
    const levels = {
      debug: 0,
      info: 1,
      warn: 2,
      error: 3
    };
    return levels[level] >= levels[this.logLevel];
  }
  logToConsole(entry) {
    if (!this.shouldLog(entry.level)) return;
    const logFn = entry.level === "error" ? console.error : entry.level === "warn" ? console.warn : entry.level === "debug" ? console.debug : console.log;
    const prefix = `[${entry.timestamp}] [${entry.level.toUpperCase()}]`;
    const message = `${prefix} ${entry.message}`;
    if (entry.requestId) {
      logFn(`${message} | Request ID: ${entry.requestId}`);
    } else {
      logFn(message);
    }
    if (entry.data) {
      logFn(`${prefix} Data:`, entry.data);
    }
    if (entry.error) {
      logFn(`${prefix} Error Details:`, this.formatError(entry.error));
    }
  }
  debug(message, data, requestId) {
    this.log("debug", message, data, requestId);
  }
  info(message, data, requestId) {
    this.log("info", message, data, requestId);
  }
  warn(message, data, requestId) {
    this.log("warn", message, data, requestId);
  }
  error(message, error, requestId) {
    if (error instanceof Error) {
      this.log("error", message, void 0, requestId, error);
    } else {
      this.log("error", message, error, requestId);
    }
  }
  log(level, message, data, requestId, error) {
    const entry = {
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      level,
      message,
      data,
      requestId,
      error
    };
    this.logToConsole(entry);
  }
}
const logger = new Logger();
function ErrorBoundary($$payload, $$props) {
  push();
  {
    $$payload.out += "<!--[!-->";
    $$payload.out += `<!---->`;
    slot($$payload, $$props, "default", {});
    $$payload.out += `<!---->`;
  }
  $$payload.out += `<!--]-->`;
  pop();
}
function _layout($$payload, $$props) {
  push();
  logger.info("Application initialized", { dev });
  ErrorBoundary($$payload, {
    children: ($$payload2) => {
      $$payload2.out += `<div class="min-h-screen bg-white dark:bg-gray-900">`;
      Navigation($$payload2);
      $$payload2.out += `<!----> <main class="max-w-7xl mx-auto px-4 py-8"><!---->`;
      slot($$payload2, $$props, "default", {});
      $$payload2.out += `<!----></main> <footer class="border-t border-gray-200 dark:border-gray-800 mt-auto"><div class="max-w-7xl mx-auto px-4 py-4 text-center text-gray-600 dark:text-gray-400">© ${escape_html((/* @__PURE__ */ new Date()).getFullYear())} Sustainability Intelligence Platform</div></footer></div>`;
    },
    $$slots: { default: true }
  });
  pop();
}
export {
  _layout as default
};
