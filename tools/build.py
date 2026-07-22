#!/usr/bin/env python3
"""
Build the static walkthrough page.

Takes the STOCK brainstem index.html (byte-identical UI) and injects one
<script> — tools/sim_shim.js — right after <body>, before any page script
runs. The shim intercepts the brainstem API + RAR CDN fetches and answers
them from an in-browser simulation, so the full 14-step "First Interview"
guided tour runs with zero dependencies.

Usage: python3 tools/build.py
Inputs (read-only):
  ~/.brainstem/src/rapp_brainstem/index.html      the stock UI
  ~/.brainstem/src/rapp_brainstem/VERSION
  ~/.brainstem/src/rapp_brainstem/agents/*.py     preinstalled sim agents
  ~/Documents/GitHub/RAR/{registry.json,agents/}  walkthrough catalog subset
Output:
  index.html (repo root)
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BRAINSTEM = os.path.expanduser("~/.brainstem/src/rapp_brainstem")
RAR = os.path.expanduser("~/Documents/GitHub/RAR")

# Agents preinstalled in the simulated agents/ folder (the stock brainstem set).
PREINSTALLED = [
    "basic_agent.py",
    "context_memory_agent.py",
    "manage_memory_agent.py",
    "hacker_news_agent.py",
]

# RAR catalog subset — every entry here is fully installable in the sim
# (its real bytes are embedded and its digest recomputed to match).
CATALOG_NAMES = [
    "@rapp/learn_new",            # required by tour step 12
    "@rapp/ping",
    "@kody-w/hello_world",
    "@rapp/hacker_news",
    "@discreetRappers/email_drafting",
    "@howardh/markdown_to_slides_agent",
    "@kody-w/context_memory_agent",
    "@kody-w/manage_memory_agent",
    "@rapp/egg_hatcher",
    "@kody-w/second_life_agent",
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    stock = read(os.path.join(BRAINSTEM, "index.html"))
    version = read(os.path.join(BRAINSTEM, "VERSION")).strip()
    shim = read(os.path.join(HERE, "sim_shim.js"))

    sim_files = {}
    for name in PREINSTALLED:
        sim_files[name] = read(os.path.join(BRAINSTEM, "agents", name))

    registry = json.load(open(os.path.join(RAR, "registry.json")))
    by_name = {a.get("name"): a for a in registry["agents"]}
    catalog, rar_files = [], {}
    for name in CATALOG_NAMES:
        entry = by_name.get(name)
        if not entry:
            # registry names drift; fall back to a loose match
            cands = [a for a in registry["agents"]
                     if name.split("/")[-1] in (a.get("name") or "")]
            if not cands:
                sys.exit(f"catalog agent not found in RAR registry: {name}")
            entry = cands[0]
        path = entry["_file"]
        content = read(os.path.join(RAR, path))
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        e = {k: entry[k] for k in
             ("name", "display_name", "description", "category", "tags",
              "_file", "_install_filename") if k in entry}
        e["_sha256"] = digest  # must match the embedded bytes, not the repo pin
        catalog.append(e)
        rar_files[path] = content

    build_stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    js = (shim
          .replace("'__SIM_BUILD__'", json.dumps(build_stamp))
          .replace("'__SIM_VERSION__'", json.dumps(version))
          .replace("__SIM_FILES__", json.dumps(sim_files))
          .replace("__SIM_CATALOG__", json.dumps(catalog))
          .replace("__SIM_RAR_FILES__", json.dumps(rar_files)))
    if "__SIM_" in js:
        sys.exit("unreplaced placeholder in shim")
    # The shim is inlined into a <script> element — a literal "</script>"
    # inside any embedded agent string would terminate it early.
    js = js.replace("</script", "<\\/script")

    marker = "<body>"
    if stock.count(marker) != 1:
        sys.exit("expected exactly one <body> in stock index.html")
    out = stock.replace(
        marker,
        marker + "\n<script>/* walkthrough simulator — see tools/sim_shim.js */\n"
        + js + "\n</script>\n<!-- WALKTHROUGH-SIM " + build_stamp
        + " brainstem-v" + version + " -->",
        1,
    )

    dest = os.path.join(REPO, "index.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {dest} ({len(out):,} bytes) — brainstem v{version}, "
          f"{len(sim_files)} preinstalled, {len(catalog)} catalog agents, build {build_stamp}")


if __name__ == "__main__":
    main()
