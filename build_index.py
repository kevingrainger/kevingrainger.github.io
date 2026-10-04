#!/usr/bin/env python3
#-------- build_index.py -------------------------------------------------------------
# Regenerates the project list of index.html from the project folders, keeping the
# page's design, header, filters, footer, script and the existing pipeline diagrams.
#
#   python build_index.py                 -> index_preview.html, images from local folders
#   python build_index.py --publish URL   -> index.html, images from the repo at URL, e.g.
#       https://raw.githubusercontent.com/kevingrainger/portfolio/main/

import html
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "index.html")

PROJECTS = [
    dict(num="001", tag="earth", tag_label="Earth systems", status="complete",
         folder="001-coral-reef-tipping-points", title="Coral reef tipping points",
         summary=["A reef modelled like a magnet: healthy coral, bleached coral, bare rock and macroalgae on a lattice, nudged by heat and by neighbours. It reproduces a real bleaching event without being steered (37% bleached in the model, 40% observed).",
                  "Reefs get stuck: once heat kills enough coral, cooling the water back does not bring it back. Mean-field models, where every patch feels every other, get stuck about 60% worse. Warming speed barely matters, and no early-warning signal fires before the slide."],
         stack="Python · Potts model · Metropolis Monte Carlo · NumPy",
         hero=("figures/cover.gif", "The reef through a heatwave and back - and the path it takes"),
         steps=[("Calibrate, unsteered", "Free-running model against 151 days of a real bleaching event: it bleaches and recovers like the reef did.", "figures/fig1_calibration.png"),
                ("Give coral a way to die", "The original could never kill coral. Mortality under prolonged heat, and seaweed held back by grazers, make collapse possible.", "figures/fig2_reef_snapshots.png"),
                ("Warm, then cool", "Hysteresis loops at 4, 8 and 12 neighbours and mean field: the further the interaction reaches, the more stuck the reef gets.", "figures/hero.png"),
                ("Speed and warnings", "Speed of warming barely matters; peak heat does. Early-warning indicators stay silent through a gradual slide.", "figures/fig3_rate_map.png")],
         results=[("figures/hero.png", "Hysteresis against interaction range"), ("figures/fig3_rate_map.png", "Warming speed vs peak heat"),
                  ("figures/fig4_early_warning.png", "No warning before a gradual collapse"), ("figures/fig1_calibration.png", "Calibration")]),
    dict(num="002", tag="earth", tag_label="Earth systems", status="complete",
         folder="002-olive-grove-xylella", title="Olive grove Xylella, stochastic SIR",
         summary=["A rebuilt agent-based model of Xylella spreading through an olive grove by spittlebug, made about 95 times faster and checked against the original. Outbreaks are all-or-nothing: 39 of 40 take the whole grove, half of it within about 2.3 years.",
                  "A sharp threshold sits between about 16% and 29% infection per spittlebug visit. Across every felling radius and detection speed tried, felling never left more trees standing; cutting spittlebug contact did the work."],
         stack="Python · agent-based modelling · ensembles · percolation threshold",
         hero=("figures/hero.png", "Five years on: no control vs fewer contacts plus felling"),
         steps=[("Rebuild, faster", "Same rules applied to every spittlebug at once: about 95x faster, and statistically identical to the original over 12 + 200 runs.", "figures/fig1_grove_day1095.png"),
                ("Find the bug that mattered", "A wrong season on day 0 gave every outbreak a head start: 38% more infection by day 600.", "figures/fig2_ensemble.png"),
                ("Find the threshold", "A visit lasts about 18 days; outbreaks die out below roughly 16-29% infection per visit and take the grove above it.", "figures/fig3_threshold.png"),
                ("Test felling", "Radius x detection speed on a 1,156-tree grove: felling removes trees faster than it stops the disease.", "figures/fig6_felling_grid.png")],
         results=[("figures/fig0_animation.gif", "Three years in twenty seconds"), ("figures/fig3_threshold.png", "All-or-nothing threshold"),
                  ("figures/fig6_felling_grid.png", "Felling grid"), ("figures/fig7_vector_control.png", "Felling vs vector control")]),
    dict(num="003", tag="signals", tag_label="Signals", status="complete",
         folder="003-corrlib-correlation-toolbox", title="corrlib, a correlation toolbox",
         summary=["A small Python library for asking how much of a correlation matrix is real: measures, estimators for messy data, factor removal, random-matrix cleaning and array stacking, behind one configurable Correlator.",
                  "Tested against known answers (59 tests). Removing the market from 40 stocks lifts the effective number of independent bets from about 7 to 15. The engine behind the seismic and solar projects."],
         stack="Python · random matrix theory · Ledoit-Wolf · pytest",
         hero=("figures/cover.png", "Forty stocks, market removed and cleaned: the sectors appear"),
         steps=[("Measure", "Pearson, rank, Gaussian-rank, partial, distance and tail-dependence measures, all one contract.", "figures/fig1_same_number_different_reality.png"),
                ("Remove", "Regress out a known factor or strip the top modes, with the noise band corrected for what was removed.", "figures/fig5_correlator_summary.png"),
                ("Clean", "Clipping, Ledoit-Wolf and nonlinear shrinkage, tested against matrices with a known truth.", "figures/fig4_noise_band.png"),
                ("Stack", "Minimum-variance weights are the Capon beamformer: one formula for portfolios and sensor arrays.", "figures/fig6_stacking.png")],
         results=[("figures/hero.png", "Sectors appear once the market is out"), ("figures/fig2_tail_dependence.png", "Crashing together"),
                  ("figures/fig3_epps_effect.png", "The Epps effect"), ("figures/fig4_noise_band.png", "Signal outside the noise band")]),
    dict(num="004", tag="signals", tag_label="Signals", status="complete",
         folder="004-seismic-denoiser", title="Seismic denoiser",
         summary=["Seismology and finance attack the same problem on 3,000 noisy recordings from the Southern California Seismic Network, scored on arrival time and first-motion direction.",
                  "The random-matrix method's 98% pick rate was a trick of every arrival sitting in the same place; move it and the rate falls to 60%. On a synthetic array, minimum-variance weighting beats averaging - once its covariance is cleaned like a stock correlation matrix."],
         stack="Python · STA/LTA · wavelets · minimum-variance beamforming · corrlib",
         hero=("figures/cover.png", "A buried wave, before and after: one sensor, the average, the optimal stack"),
         steps=[("Calibrate on quiet traces", "Picker and first-motion estimator agree with analysts on 99% and 97% of clean recordings.", "figures/fig1_one_trace.png"),
                ("Score on noisy ones", "Five methods, with and without a random shift of the arrival.", "figures/fig2_scoreboard.png"),
                ("Stack an array", "Sensors near a road share noise; the covariance finds and cancels it.", "figures/fig3_array.png"),
                ("How much data?", "Raw optimal weights need ~0.8 s of noise to beat averaging; cleaned weights win from 0.2 s.", "figures/fig4_crossover.png")],
         results=[("figures/fig2_scoreboard.png", "Scoreboard"), ("figures/fig1_one_trace.png", "One noisy trace"),
                  ("figures/fig4_crossover.png", "The crossover"), ("figures/hero.png", "Gain against array size")]),
    dict(num="005", tag="markets", tag_label="Markets", status="complete",
         folder="005-option-pricer", title="Option pricer: European, American, Asian",
         summary=["Time-varying volatility from a real S&P 500 option chain, a finite-difference solver converging at order 2.09, American puts by projected SOR, SET50 against the S&P 500, and Asian options on coffee, cocoa and sugar.",
                  "The surprise: an Asian option's delta fades as the average locks in, yet it is no easier to hedge - its risk concentrates just before averaging starts. Ignoring seasonal volatility misprices it but leaves the hedge intact."],
         stack="Python · Crank-Nicolson/SOR · Monte Carlo · control variates · delta hedging",
         hero=("figures/cover.png", "Monte Carlo: simulated coffee prices and the average an Asian option pays on"),
         steps=[("Read the market", "Forward, discount and forward volatility straight out of an S&P 500 chain via put-call parity.", "figures/fig1_forward_volatility.png"),
                ("Check the solver", "Second-order convergence measured, American puts against a binomial tree.", "figures/fig2_pde_convergence.png"),
                ("Bangkok vs New York", "SET50: more volatile, fatter-tailed, a steeper implied skew.", "figures/fig4_set50_skew.png"),
                ("Price and hedge an Asian", "Control variate cuts the noise 1,100-7,200x; a hedge simulator finds where the risk lives.", "figures/fig10_hedging_risk_timing.png")],
         results=[("figures/fig9_control_variate.png", "The control variate"), ("figures/fig3_american_boundary.png", "Early-exercise boundary"),
                  ("figures/fig4_set50_skew.png", "SET50 vs S&P 500 skew"), ("figures/fig8_seasonal_vol.png", "Seasonal volatility in softs")]),
    dict(num="006", tag="markets", tag_label="Markets", status="pipeline built",
         folder="006-italian-power-volatility", title="Italian power price volatility",
         summary=["Three stages: what drives the Italian power price (XGBoost and SHAP, with gas taken out first), what drives its volatility (GARCH-MIDAS), and how many months ahead a weather forecast still helps.",
                  "Built and checked on a placeholder with planted relationships: the estimator is unbiased but imprecise, and a modest weather effect needs a long test period to detect. Real GME and ERA5 series next."],
         stack="Python · XGBoost · SHAP · GARCH-MIDAS · Diebold-Mariano",
         hero=("figures/cover.png", "Price history and a nine-month projection across 300 weather scenarios (placeholder data)"),
         steps=[("Weather to price", "Gas-relative target; SHAP recovers the heating and cooling U-shape.", "figures/fig2_shap.png"),
                ("Weather to volatility", "GARCH-MIDAS recovers the planted weather effect on average over ten simulated decades.", "figures/fig3_midas_recovery.png"),
                ("Forecast to volatility", "With a strong effect, forecasts help out to about 1-2 months.", "figures/hero.png")],
         results=[("figures/fig1_price_and_weather.png", "Price and extreme weather"), ("figures/fig4_volatility_components.png", "Volatility components"),
                  ("figures/fig3_midas_recovery.png", "Estimator check"), ("figures/hero.png", "Forecast horizon")]),
    dict(num="007", tag="markets", tag_label="Markets", status="in progress",
         folder="007-spanish-solar-portfolio", title="Spanish solar portfolio strategy",
         summary=["How far does a cloud reach? An Anemoi ML-ready ERA5 dataset for Iberia, built with tested data-quality checks, CI and Docker, feeds a seasonal analysis of how correlated 25 Spanish solar sites are - the diversification a solar fleet really has.",
                  "On ERA5 2023 the weather stays correlated over 350-670 km, so 25 sites behave like 3-4. A shared daily artefact, invisible on synthetic data, had to be removed first. Next: CERRA at 5.5 km, prices and cannibalisation, and AI (AIFS) versus physics forecasts scored in money."],
         stack="Python · anemoi-datasets · ERA5 · Zarr · pvlib · corrlib · CI/CD",
         hero=("figures/cover.png", "Correlation with Seville by season, and against distance for every site pair"),
         steps=[("Build the dataset", "ERA5 GRIB to an Anemoi Zarr dataset over Iberia, with quality checks written as tests.", "figures/fig1_two_weeks.png"),
                ("Measure the reach", "Correlation of clear-sky index against distance, by season.", "figures/fig2_correlation_vs_distance.png"),
                ("Remove the sun", "A daily shape every site shares, left by the clear-sky model, is subtracted before correlating.", "figures/fig0_daily_shape.png"),
                ("Month by month", "The same fit for each month of 2023.", "figures/fig3_monthly_reach.png"),
                ("Count independent sites", "Effective number of sites, raw and cleaned, by season.", "figures/fig4_effective_sites.png")],
         results=[("figures/hero.png", "The reach of the weather"), ("figures/fig2_correlation_vs_distance.png", "Correlation against distance"),
                  ("figures/fig4_effective_sites.png", "Effective sites by season"), ("figures/fig3_monthly_reach.png", "Month by month")]),
]


EXTRA_CSS = '\n  <style>\n    /* covers and figures: full width, uncropped, high resolution */\n    .wrap { max-width: 1120px; }\n    .detail { flex-direction: column; gap: 1.25rem; }\n    .detail > figure { flex: none; width: 100%; }\n    figure img { aspect-ratio: auto; object-fit: contain; background: #fff; }\n    .detail > figure img { border: 1px solid var(--rule); }\n    .results { grid-template-columns: repeat(auto-fit, minmax(30rem, 1fr)); gap: 2rem; }\n    .step { grid-template-columns: minmax(0, 1fr) 460px; }\n    @media (max-width: 900px) { .step { grid-template-columns: 1fr; } .results { grid-template-columns: 1fr; } }\n  </style>\n</head>'


# Earlier (college) work: a compact list under the projects, some without a picture
EARLIER = [
    dict(folder="earlier-work/pde-solvers-cpp", title="PDEs by successive over-relaxation",
         text="Laplace's equation in C++ with SOR, the cost surface over the relaxation factor, a Schrödinger study, and a new Black-Scholes solver (Crank-Nicolson + projected SOR, Numba).",
         stack="C++ · Python · Numba", img="figures/cover.png"),
    dict(folder="earlier-work/potts-monte-carlo-cpp", title="The Potts model by Monte Carlo",
         text="Metropolis Monte Carlo for the 3-state Potts model; fluctuations peak near the exact critical point. The seed of the coral reef project.",
         stack="C++", img="figures/fig1_transition.png"),
    dict(folder="earlier-work/higher-order-odes-cpp", title="Higher-order ODEs",
         text="Fourth-order Runge-Kutta and the shooting method; the error falls as h^4, as it should.",
         stack="C++", img=None),
]

EARLIER_CSS = """
  <style>
    .earlier { margin: 3rem 0 2rem; border-top: 1px solid var(--rule); padding-top: 1.25rem; }
    .earlier h2 { font-size: 1rem; letter-spacing: .04em; text-transform: uppercase; margin: 0 0 1rem; }
    .earlier ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 1.25rem; }
    .earlier li { display: grid; grid-template-columns: minmax(0, 1fr) 260px; gap: 1.25rem; align-items: start; }
    .earlier li.noimg { grid-template-columns: 1fr; }
    .earlier h3 { font-size: 1rem; margin: 0 0 .3rem; }
    .earlier p { margin: 0 0 .3rem; font-size: .92rem; }
    .earlier .stack { opacity: .7; font-size: .85rem; }
    .earlier img { width: 100%; height: auto; border: 1px solid var(--rule); background: #fff; }
    @media (max-width: 700px) { .earlier li { grid-template-columns: 1fr; } }
  </style>
</head>"""


def earlier_html(base, publish):
    rows = []
    for e in EARLIER:
        link = (base.replace("raw.githubusercontent.com", "github.com").replace("/main/", "/tree/main/") + e["folder"]) if publish \
            else f"{base}{e['folder']}/README.md"
        img = (f'<a href="{html.escape(link)}"><img src="{html.escape(base + e["folder"] + "/" + e["img"])}" '
               f'alt="{html.escape(e["title"])}" loading="lazy"></a>') if e["img"] else ""
        rows.append(f'      <li{"" if img else " class=\"noimg\""}><div><h3><a href="{html.escape(link)}">{html.escape(e["title"])}</a></h3>'
                    f'<p>{html.escape(e["text"])}</p><p class="stack">{html.escape(e["stack"])}</p></div>{img}</li>')
    return ('\n  <section class="earlier">\n    <h2>Earlier work</h2>\n    <ul>\n' + "\n".join(rows) +
            '\n    </ul>\n  </section>\n')


# Credit lines rewritten to match what each project now actually does
CREDITS = {
    '001': '<p class="credit"><sup>&dagger;</sup>Builds on Mumby, Hastings &amp; Edwards (2007). Bleaching record from Scott Reef, Western Australia.</p>',
    '002': '<p class="credit"><sup>&dagger;</sup>Recreation of <a href="https://doi.org/10.1038/s41598-019-44997-4">Fierro, Liccardo &amp; Porcelli (2019)</a>, <em>Scientific Reports</em>.</p>',
    '003': '<p class="credit"><sup>&dagger;</sup>Builds on Epps (1979), Laloux, Cizeau, Bouchaud &amp; Potters (1999), Ledoit &amp; Wolf (2004, 2020) and Capon (1969). Prices from Yahoo Finance via yfinance.</p>',
    '004': '<p class="credit"><sup>&dagger;</sup>STA/LTA from Allen (1978); optimal array weights from Capon (1969). Labelled waveforms from <a href="https://doi.org/10.1029/2017JB015251">Ross, Meier &amp; Hauksson (2018)</a>, Southern California Seismic Network data via the <a href="https://doi.org/10.7909/C3WD3xH1">SCEDC</a>.</p>',
    '005': '<p class="credit"><sup>&dagger;</sup>Control variate from Kemna &amp; Vorst (1990). Projected SOR as in Wilmott, Howison &amp; Dewynne (1995). Prices from Yahoo Finance via yfinance; SET50 history from Investing.com.</p>',
    '006': '<p class="credit"><sup>&dagger;</sup>Builds on Guerzoni, Riso &amp; Zoia (2026). GARCH-MIDAS from Engle, Ghysels &amp; Sohn (2013).</p>',
    '007': '<p class="credit"><sup>&dagger;</sup>Weather from ERA5 (<a href="https://doi.org/10.1002/qj.3803">Hersbach et al. 2020</a>), built with ECMWF\'s anemoi-datasets. Contains modified Copernicus Climate Change Service information (2023). Capture-rate framing from Hirth (2013).</p>',
}

# Pipeline-tab notes written before the code existed, brought up to date
PIPELINE_FIXES = [
    ("<b>Output (planned).</b>", "<b>Output.</b>"),
    ('<p class="flow-note">Steps 1–2 are the code in the repo now; steps 3–4 are the planned scoreboard.</p>', ""),
    ('<p class="flow-note">Planned structure; Asian pricing and the SET50 calibration are still being built.</p>', ""),
    ('<p class="flow-note">Planned structure.</p><ol class="flow"><li><b>Input.</b> GME',
     '<p class="flow-note">The plan for real data; the code currently runs on a placeholder of the same shape.</p><ol class="flow"><li><b>Input.</b> GME'),
    ('<p class="flow-note">Planned structure.</p><ol class="flow"><li><b>Input.</b> Hourly ERA5',
     '<p class="flow-note">The full plan; the first stage, how correlated the sites are, is done.</p><ol class="flow"><li><b>Input.</b> Hourly ERA5'),
]


def fig(src, caption, base, folder, lazy=True):
    url = f"{base}{folder}/{src}"
    return (f'<figure><img src="{html.escape(url)}" alt="{html.escape(caption)}"'
            f'{" loading=\"lazy\"" if lazy else ""}><figcaption>{html.escape(caption)}</figcaption></figure>')


def project_html(p, base, credit, pipeline_panel, repo_link):
    n = p["num"]
    steps = "\n".join(
        f'<li class="step"><div><h5><span class="sn">{i:02d}</span>{html.escape(t)}</h5><p>{html.escape(d)}</p></div>'
        f'{fig(f_, t, base, p["folder"])}</li>' for i, (t, d, f_) in enumerate(p["steps"], 1))
    results = "".join(fig(f_, c, base, p["folder"]) for f_, c in p["results"])
    summary = "\n".join(f"            <p>{html.escape(s)}</p>" for s in p["summary"])
    pipeline_tab = (f'<button type="button" role="tab" id="t-{n}-pipeline" aria-controls="p-{n}-pipeline" '
                    f'aria-selected="false" tabindex="-1">pipeline</button>') if pipeline_panel else ""
    return f'''    <li class="project" data-tag="{p["tag"]}">
      <button class="project-head" type="button" aria-expanded="false">
        <span class="num">{n}</span><span class="title">{html.escape(p["title"])}</span>
        <span class="tag">{p["tag_label"]}</span><span class="status">{p["status"]}</span>
      </button>
      <div class="more"><div>
        <div class="detail">
          <div class="text">
{summary}
            {credit}
            <p class="stack">{html.escape(p["stack"])}</p>
            <a class="gh" href="{html.escape(repo_link)}">Read the write-up and code</a><br>
            <button class="view-more" type="button" aria-expanded="false" aria-controls="ext-{n}">+ view more</button>
          </div>
          {fig(p["hero"][0], p["hero"][1], base, p["folder"], lazy=False)}
        </div>
        <div class="ext" id="ext-{n}" hidden>
          <div class="tabs" role="tablist" aria-label="{html.escape(p["title"])} sections">
            <button type="button" role="tab" id="t-{n}-method" aria-controls="p-{n}-method" aria-selected="true">method</button>
            <button type="button" role="tab" id="t-{n}-results" aria-controls="p-{n}-results" aria-selected="false" tabindex="-1">results</button>
            {pipeline_tab}
          </div>
          <div class="panel" role="tabpanel" id="p-{n}-method" aria-labelledby="t-{n}-method">
            <ol class="timeline">
{steps}
            </ol>
          </div>
          <div class="panel" role="tabpanel" id="p-{n}-results" aria-labelledby="t-{n}-results" hidden>
            <div class="results">{results}</div>
          </div>
          {pipeline_panel}
        </div>
      </div></div>
    </li>'''


def main():
    publish = "--publish" in sys.argv
    base = sys.argv[sys.argv.index("--publish") + 1] if publish else "../"
    page = io.open(SOURCE, encoding="utf8").read()
    #index.html may already be a built page: drop what a previous build added, so re-running is safe
    page = page.replace(EARLIER_CSS, "</head>").replace(EXTRA_CSS, "</head>")
    page = re.sub(r'\n  <section class="earlier">.*?</section>\n', "", page, flags=re.S)

    start = page.index('<ul class="projects">') + len('<ul class="projects">')
    end = page.index("</ul>", start)
    old_list = page[start:end]

    items = []
    for p in PROJECTS:
        n = p["num"]
        block_start = old_list.index(f'<span class="num">{n}</span>')
        next_item = old_list.find('<li class="project"', block_start)
        block = old_list[block_start:next_item if next_item > 0 else len(old_list)]
        credit = re.search(r'<p class="credit">.*?</p>', block, re.S)
        credit = CREDITS.get(n, credit.group(0) if credit else "")
        pipe_start = block.find(f'<div class="panel" role="tabpanel" id="p-{n}-pipeline"')
        pipeline_panel = ""
        if pipe_start >= 0:
            pipe_end = block.index("\n        </div>\n      </div></div>", pipe_start)
            pipeline_panel = block[pipe_start:pipe_end]
        repo_link = f"{base}{p['folder']}/README.md" if not publish else \
            base.replace("raw.githubusercontent.com", "github.com").replace("/main/", "/tree/main/") + p["folder"]
        items.append(project_html(p, base, credit, pipeline_panel, repo_link))

    after = end + len("</ul>")
    new_page = page[:start] + "\n" + "\n".join(items) + "\n  </ul>" + earlier_html(base, publish) + page[after:]
    new_page = new_page.replace("</head>", EXTRA_CSS, 1).replace("</head>", EARLIER_CSS, 1)
    for old, new in PIPELINE_FIXES:
        new_page = new_page.replace(old, new)
    new_page = new_page.replace(" All are side projects, built for fun.", "")
    new_page = new_page.replace("Most start from someone else's\n    published model and try to add one honest result.",
                                "Most start from someone else's\n    published model and try to add one honest result. All are side projects, built for fun.")
    out = os.path.join(HERE, "index.html" if publish else "index_preview.html")
    io.open(out, "w", encoding="utf8").write(new_page)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
