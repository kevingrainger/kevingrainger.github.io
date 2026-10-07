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
    dict(num="003", tag="earth", tag_label="Earth systems", status="pipeline built",
         folder="003-po-valley-downscaling", title="Po Valley temperature at 1 km, physics-anchored",
         summary=["What is the temperature between the weather stations? Daily maximum temperature on a 1 km grid: between stations the surface obeys a reduced heat-budget equation in which each land-cover class couples the air to the ground at its own rate; at stations it equals the reading exactly. XGBoost learns the heating the equation lacks and hands it back as a prior.",
                  "Built and checked on placeholder daily fields with real station locations. The constraint holds to within a trillionth of a kelvin on every day. At held-out 50 km blocks the error falls from 1.34 K (ERA5-Land) to 0.79 K, level with regression-kriging at 0.85 K rather than clearly ahead of it. The physics turns out to be local, a few kilometres; the reach comes from the statistics. Real ERA5-Land, MODIS and station data next."],
         stack="Python · sparse PDE solver · adjoint gradients · variational anchoring · XGBoost · folium",
         hero=("figures/cover.png", "Downscaled daily maximum temperature draped over the terrain, hottest July 2022 day (placeholder data)"),
         steps=[("Test the solver first", "A fake truth built from the PDE itself: planted parameters come back exactly when the physics is complete, within 25% when it is not.", "figures/fig0_step0_recovery.png"),
                ("Anchor the surface", "One adjoint solve per station gives its footprint; the smallest, smoothest forcing that makes the surface equal every station follows in closed form.", "figures/hero.png"),
                ("Hold out whole blocks", "Stations in 50 km blocks are left out together and scored in a year never used for fitting, against four baselines.", "figures/fig3_skill.png"),
                ("Read the missing physics", "The forcing the equation needed, averaged over all days, beside the land-cover map.", "figures/fig5_missing_physics.png")],
         results=[("figures/fig2_heatwave_day.png", "ERA5-Land, the anchored model and the hidden truth"), ("figures/fig3_skill.png", "Skill at held-out stations"),
                  ("figures/fig4_footprints.png", "Station footprints, calm and windy"), ("figures/fig1_stations.png", "The station network")],
         maps=[("maps/003-heatwave.html", "Interactive: the heatwave day at 1 km against ERA5-Land, with every station."),
               ("maps/003-missing-physics.html", "Interactive: missing heating, land cover and station footprints.")]),
    dict(num="004", tag="signals", tag_label="Signals", status="complete",
         folder="004-corrlib-correlation-toolbox", title="corrlib, a correlation toolbox",
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
    dict(num="005", tag="signals", tag_label="Signals", status="complete",
         folder="005-seismic-denoiser", title="Seismic denoiser",
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
    dict(num="006", tag="markets", tag_label="Markets", status="complete",
         folder="006-option-pricer", title="Option pricer: European, American, Asian",
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
    dict(num="007", tag="markets", tag_label="Markets", status="pipeline built",
         folder="007-italian-power-volatility", title="Italian power price volatility",
         summary=["Three stages: what drives the Italian power price (XGBoost and SHAP, with gas taken out first), what drives its volatility (GARCH-MIDAS), and how many months ahead a weather forecast still helps.",
                  "Built and checked on a placeholder with planted relationships: the estimator is unbiased but imprecise, and a modest weather effect needs a long test period to detect. Real GME and ERA5 series next."],
         stack="Python · XGBoost · SHAP · GARCH-MIDAS · Diebold-Mariano",
         hero=("figures/cover.png", "Price history and a nine-month projection across 300 weather scenarios (placeholder data)"),
         steps=[("Weather to price", "Gas-relative target; SHAP recovers the heating and cooling U-shape.", "figures/fig2_shap.png"),
                ("Weather to volatility", "GARCH-MIDAS recovers the planted weather effect on average over ten simulated decades.", "figures/fig3_midas_recovery.png"),
                ("Forecast to volatility", "With a strong effect, forecasts help out to about 1-2 months.", "figures/hero.png")],
         results=[("figures/fig1_price_and_weather.png", "Price and extreme weather"), ("figures/fig4_volatility_components.png", "Volatility components"),
                  ("figures/fig3_midas_recovery.png", "Estimator check"), ("figures/hero.png", "Forecast horizon")]),
    dict(num="008", tag="markets", tag_label="Markets", status="in progress",
         folder="008-spanish-solar-portfolio", title="Spanish solar portfolio strategy",
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
    #-------- undergraduate work, presented the same way --------------------------------
    dict(num="009", tag="physics", tag_label="Physics", status="undergrad",
         folder="earlier-work/pde-solvers-cpp", title="PDEs by successive over-relaxation",
         summary=["Laplace's equation on a square holding a charged box and a grounded wire, solved in C++ by successive over-relaxation, then ported to Python with Numba to map how the cost depends on the relaxation factor and the grid size.",
                  "The same machinery prices options: Black-Scholes by Crank-Nicolson with SOR, and American puts by projected SOR, which traces the early-exercise boundary for free. It matches the closed form to within 0.003. Also here: a numerical study of the Schrödinger equation."],
         stack="C++ · Python · Numba · finite differences · SOR",
         hero=("figures/cover.png", "Laplace's equation solved by SOR: surface and contours"),
         steps=[("Solve Laplace's equation", "Over-relaxed Gauss-Seidel sweeps on a 253 x 253 grid: 760 sweeps at the optimal factor, against 4,047 at 1.8.", "figures/fig1_laplace_surface.png"),
                ("Map the cost", "Sweeps to converge across relaxation factor and grid size; the best factor climbs towards 2 as the grid refines.", "figures/fig2_sor_parameter_surface.png"),
                ("Price an option", "Black-Scholes stepped back from expiry by Crank-Nicolson; projected SOR for the American put.", "figures/fig3_black_scholes_surfaces.png"),
                ("Check it", "Against the closed-form price, and the early-exercise boundary through time.", "figures/fig4_black_scholes_check.png")],
         results=[("figures/fig2_sor_parameter_surface.png", "SOR cost surface"), ("figures/fig3_black_scholes_surfaces.png", "Black-Scholes surfaces"),
                  ("figures/fig4_black_scholes_check.png", "Validation and exercise boundary"), ("figures/original_pde_surfaces.png", "The original C++ surfaces")]),
    dict(num="010", tag="physics", tag_label="Physics", status="undergrad",
         folder="earlier-work/potts-monte-carlo-cpp", title="The Potts model by Monte Carlo",
         summary=["A grid where every site holds one of three states and prefers to match its neighbours, sampled by Metropolis Monte Carlo in C++. Hot, it is noise; cold, one state takes over; at the critical point, domains of every size appear at once.",
                  "Fluctuations peak at β ≈ 1.04, close to the exact critical point ln(1 + √3) ≈ 1.005 for a 24 x 24 lattice. The same model, scaled up, became the coral reef project."],
         stack="C++ · Python · Numba · Metropolis Monte Carlo · statistical physics",
         hero=("figures/cover.png", "The lattice hot, at the critical point, and cold"),
         steps=[("Simulate the lattice", "Single-site Metropolis updates; snapshots from a 256 x 256 Numba port.", "figures/fig1_lattice.png"),
                ("Watch order appear", "Magnetisation jumps from about 0.1 to 0.9 over a narrow range of temperature.", "figures/fig2_magnetisation.png"),
                ("Find the transition", "Fluctuations peak at the critical point.", "figures/fig3_fluctuations.png")],
         results=[("figures/fig1_lattice.png", "Cooling through the transition"), ("figures/fig2_magnetisation.png", "Magnetisation"),
                  ("figures/fig3_fluctuations.png", "Fluctuations"), ("figures/original_potts_results.png", "The original C++ results")]),
    dict(num="011", tag="physics", tag_label="Physics", status="undergrad",
         folder="earlier-work/higher-order-odes-cpp", title="Higher-order ODEs and the shooting method",
         summary=["A hand-written fourth-order Runge-Kutta integrator in C++, checked against an exact solution, extended to a fourth-order equation by rewriting it as four first-order ones.",
                  "The error falls as the fourth power of the step (fitted slope 3.95). The shooting method turns a boundary-value problem into a target practice: guess the starting slope, integrate, bisect on the miss - 25 shots to hit x(10) = -1."],
         stack="C++ · Python · Runge-Kutta · shooting method · bisection",
         hero=("figures/cover.png", "The shooting method closing in on a boundary condition"),
         steps=[("Step it forward", "RK4 against the exact solution of dx/dt = (t - 2)²(x + 1).", "figures/fig1_rk4_vs_exact.png"),
                ("Measure the order", "Halve the step, cut the error sixteen-fold.", "figures/fig2_convergence.png"),
                ("Go higher order", "A fourth-order equation as four coupled first-order ones.", "figures/fig3_fourth_order.png"),
                ("Shoot", "Bisect on the starting slope until the far boundary is hit.", "figures/fig4_shooting.png")],
         results=[("figures/fig4_shooting.png", "Shooting method"), ("figures/fig2_convergence.png", "Fourth-order convergence"),
                  ("figures/fig1_rk4_vs_exact.png", "RK4 against the exact answer"), ("figures/fig3_fourth_order.png", "A fourth-order ODE")]),
]


EXTRA_CSS = '\n  <style>\n    /* covers and figures: full width, uncropped, high resolution */\n    .wrap { max-width: 1120px; }\n    .detail { flex-direction: column; gap: 1.25rem; }\n    .detail > figure { flex: none; width: 100%; }\n    figure img { aspect-ratio: auto; object-fit: contain; background: #fff; }\n    .detail > figure img { border: 1px solid var(--rule); }\n    .results { grid-template-columns: repeat(auto-fit, minmax(30rem, 1fr)); gap: 2rem; }\n    .live { margin: 0 0 2rem; } .live iframe { display: block; width: 100%; height: 520px; border: 1px solid var(--rule); background: #fff; }\n    .step { grid-template-columns: minmax(0, 1fr) 460px; }\n    @media (max-width: 900px) { .step { grid-template-columns: 1fr; } .results { grid-template-columns: 1fr; } }\n  </style>\n</head>'


# Style block from an older build that listed earlier work separately; kept only so
# re-running on that page strips it out
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



# Credit lines rewritten to match what each project now actually does
CREDITS = {
    '001': '<p class="credit"><sup>&dagger;</sup>Builds on Mumby, Hastings &amp; Edwards (2007). Bleaching record from Scott Reef, Western Australia; sea temperatures from NOAA Coral Reef Watch and the Australian Institute of Marine Science (AIMS).</p>',
    '002': '<p class="credit"><sup>&dagger;</sup>Recreation of <a href="https://doi.org/10.1038/s41598-019-44997-4">Fierro, Liccardo &amp; Porcelli (2019)</a>, <em>Scientific Reports</em>.</p>',
    '003': '<p class="credit"><sup>&dagger;</sup>Variational analysis from Sasaki (1970) and Lorenc (1986). Positioned against E-OBS (<a href="https://doi.org/10.1029/2017JD028200">Cornes et al. 2018</a>) and ERA5-Land (<a href="https://doi.org/10.5194/essd-13-4349-2021">Mu&ntilde;oz-Sabater et al. 2021</a>); closest published relative <a href="https://doi.org/10.3390/cli10030047">Wilson et al. (2022)</a>, First Street Foundation. XGBoost from Chen &amp; Guestrin (2016). Station list from Meteostat.</p>',
    '004': '<p class="credit"><sup>&dagger;</sup>Builds on Epps (1979), Laloux, Cizeau, Bouchaud &amp; Potters (1999), Ledoit &amp; Wolf (2004, 2020) and Capon (1969). Prices from Yahoo Finance via yfinance.</p>',
    '005': '<p class="credit"><sup>&dagger;</sup>STA/LTA from Allen (1978); optimal array weights from Capon (1969). Labelled waveforms from <a href="https://doi.org/10.1029/2017JB015251">Ross, Meier &amp; Hauksson (2018)</a>, Southern California Seismic Network data via the <a href="https://doi.org/10.7909/C3WD3xH1">SCEDC</a>.</p>',
    '006': '<p class="credit"><sup>&dagger;</sup>Control variate from Kemna &amp; Vorst (1990). Projected SOR as in Wilmott, Howison &amp; Dewynne (1995). Prices from Yahoo Finance via yfinance; SET50 history from Investing.com.</p>',
    '009': '<p class="credit"><sup>&dagger;</sup>Projected SOR as in Wilmott, Howison &amp; Dewynne (1995).</p>',
    '010': '<p class="credit"><sup>&dagger;</sup>Exact critical point from Baxter (1973); Metropolis et al. (1953).</p>',
    '011': '',
    '007': '<p class="credit"><sup>&dagger;</sup>Builds on Guerzoni, Riso &amp; Zoia (2026). GARCH-MIDAS from Engle, Ghysels &amp; Sohn (2013).</p>',
    '008': '<p class="credit"><sup>&dagger;</sup>Weather from ERA5 (<a href="https://doi.org/10.1002/qj.3803">Hersbach et al. 2020</a>), built with ECMWF\'s anemoi-datasets. Contains modified Copernicus Climate Change Service information (2023). Capture-rate framing from Hirth (2013).</p>',
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


#-------- pipeline panels for projects added after the page was first designed ---------------
# Same markup as the hand-built panels: boxes on a five-column grid, edges that carry
# data-from / data-to so the page's trace script can follow them.
def draw_pipeline(n, title, stages, nodes, edges, note, flow):
    X = lambda s: 12 + 200 * s
    Y = lambda r: 56 + 92 * r
    pos = {i: (X(s), Y(r)) for i, _, _, s, r, _ in nodes}
    rows = 1 + max(r for *_, r, _ in nodes)
    out = [f'<svg class="map" viewBox="0 0 1000 {30 + 92 * rows}" width="100%" role="img" aria-label="{html.escape(title)}" xmlns="http://www.w3.org/2000/svg">',
           f'<defs><marker id="ah{n}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" fill="#2430bc"/></marker>'
           f'<marker id="am{n}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" fill="#6a6a70"/></marker></defs>']
    out += [f'<text x="{X(i)}" y="22" font-size="11" letter-spacing="1.5" fill="#6a6a70">{html.escape(s.upper())}</text>' for i, s in enumerate(stages)]
    for a, c, main in edges:
        (x1, y1), (x2, y2) = pos[a], pos[c]
        if x1 == x2:                                   # same column: straight down or up
            d = f"M{x1 + 79} {y1 + 50}L{x1 + 79} {y2 - 2}" if y2 > y1 else f"M{x1 + 79} {y1}L{x1 + 79} {y2 + 52}"
        else:                                          # across columns: out of the right side, elbow, into the left side
            mid = x1 + 158 + (x2 - x1 - 158) / 2
            yin = y2 + 25 if y1 == y2 else y2 + (38 if y1 > y2 else 12)
            d = f"M{x1 + 158} {y1 + 25}L{mid} {y1 + 25}L{mid} {yin}L{x2 - 2} {yin}"
        colour, width, mark = ("#2430bc", "1.4", "ah") if main else ("#6a6a70", "1", "am")
        out.append(f'<path class="edge" data-from="{a}" data-to="{c}" d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" marker-end="url(#{mark}{n})"/>')
    for i, label, sub, s, r, kind in nodes:
        x, y = pos[i]
        rect = {"input": 'fill="#ffffff" stroke="#cfcdc5" stroke-dasharray="4 3"', "step": 'fill="#ffffff" stroke="#cfcdc5"',
                "output": 'fill="#eceefb" stroke="#2430bc"'}[kind]
        ink = "#2430bc" if kind == "output" else "#1b1b1f"
        out.append(f'<g class="node" data-id="{i}" tabindex="0" role="button" aria-label="{html.escape(label)}: {html.escape(sub)}. Highlight its path">'
                   f'<rect x="{x}" y="{y}" width="158" height="50" rx="3" {rect}/><text x="{x + 10}" y="{y + 21}" font-size="12.5" fill="{ink}">{html.escape(label)}</text>'
                   f'<text x="{x + 10}" y="{y + 38}" font-size="10.5" fill="#6a6a70">{html.escape(sub)}</text></g>')
    out.append("</svg>")
    steps = "".join(f"<li><b>{html.escape(h)}.</b> {html.escape(t)}</li>" for h, t in flow)
    return (f'<div class="panel" role="tabpanel" id="p-{n}-pipeline" aria-labelledby="t-{n}-pipeline" hidden>\n'
            f'            <p class="hint">Hover or tab to a box to trace everything that feeds into it and everything it feeds.</p>\n'
            f'            <div class="pipe">{"".join(out)}</div>\n'
            f'            <h5 class="flow-head">How the data flows</h5>\n'
            f'            <p class="flow-note">{html.escape(note)}</p><ol class="flow">{steps}</ol>\n'
            f'          </div>')


NEW_PIPELINES = {
    "003": lambda: draw_pipeline(
        "003", "Po Valley Tmax: physics-anchored downscaling",
        ["Inputs", "Daily fields", "Physics", "Anchor and learn", "Outputs"],
        [("era", "ERA5-Land", "Tmax, skin T, wind", 0, 0, "input"), ("lst", "MODIS LST", "Aqua, 1 km, gaps", 0, 1, "input"),
         ("static", "Terrain, land cover", "GLO-30, WorldCover", 0, 2, "input"),
         ("red", "Sea-level reduction", "θ = T + Γz", 1, 0, "step"), ("gap", "Cloud-gap fill", "skin T + offset", 1, 1, "step"),
         ("taus", "Surface coupling", "rates add by class", 1, 2, "step"),
         ("fit", "Adjoint fit", "κ, τ by land cover", 2, 0, "step"), ("pde", "Heat-budget PDE", "A θ = b + q", 2, 1, "step"),
         ("st", "Stations", "Meteostat Tmax", 3, 0, "input"), ("anc", "Anchored solve", "H θ = y exactly", 3, 1, "step"),
         ("xgb", "XGBoost", "learns q", 3, 2, "step"),
         ("cv", "Blocked hold-out", "2023, 50 km blocks", 4, 0, "output"), ("tmax", "Tmax at 1 km", "every station exact", 4, 1, "output"),
         ("q", "Missing physics", "mean q map", 4, 2, "output")],
        [("era", "red", True), ("lst", "gap", True), ("static", "taus", True), ("red", "gap", False), ("red", "fit", False),
         ("gap", "pde", True), ("taus", "pde", False), ("fit", "pde", False), ("pde", "anc", True), ("st", "anc", True),
         ("anc", "xgb", True), ("st", "cv", False), ("anc", "tmax", True), ("xgb", "q", True)],
        "The code runs end to end on placeholder daily fields of the same shape; the download script for the real products ships with it.",
        [("Input", "ERA5-Land daily maximum temperature, skin temperature and afternoon wind at 0.1°; MODIS Aqua daytime land surface temperature at 1 km; elevation and six land-cover fractions per 1 km cell; station daily maxima."),
         ("Daily fields", "Everything is reduced to sea level with a 6.5 K/km lapse rate. Cloud gaps in the MODIS field are filled with ERA5-Land skin temperature plus each cell's mean clear-sky offset for the month."),
         ("Physics", "A steady advection-diffusion-relaxation equation is assembled as a sparse system and factorised once per day. Its relaxation times, one per land-cover class, are fitted with adjoint gradients."),
         ("Anchor and learn", "One adjoint solve per station gives its footprint. The smallest, smoothest forcing q that makes the surface equal every station is found in closed form; XGBoost learns q from land cover and terrain and supplies it as a prior."),
         ("Output", "Daily maximum temperature at 1 km that returns every station reading exactly, a map of the heating the equation lacks, and a skill table from 50 km blocks held out in a year never used for fitting.")]),
}


def fig(src, caption, base, folder, lazy=True):
    url = f"{base}{folder}/{src}"
    return (f'<figure><img src="{html.escape(url)}" alt="{html.escape(caption)}"'
            f'{" loading=\"lazy\"" if lazy else ""}><figcaption>{html.escape(caption)}</figcaption></figure>')


def project_html(p, base, credit, pipeline_panel, repo_link):
    n = p["num"]
    #interactive maps live in this site's own maps/ folder and are embedded, not linked
    maps = "".join(f'<figure class="live"><iframe src="{html.escape(src)}" title="{html.escape(c)}" loading="lazy"></iframe>'
                   f'<figcaption>{html.escape(c)} <a href="{html.escape(src)}">Open full screen</a></figcaption></figure>' for src, c in p.get("maps", []))
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
            {maps}<div class="results">{results}</div>
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
    page = re.sub(r'\n  <style>\n    /\* covers and figures:.*?</style>\n</head>', "</head>", page, flags=re.S)   # an older build's version of it
    page = re.sub(r'\n  <section class="earlier">.*?</section>\n', "", page, flags=re.S)

    start = page.index('<ul class="projects">') + len('<ul class="projects">')
    end = page.index("</ul>", start)
    old_list = page[start:end]

    items = []
    for p in PROJECTS:
        n = p["num"]
        block_start = old_list.find(f'<span class="num">{n}</span>')
        next_item = old_list.find('<li class="project"', block_start)
        block = "" if block_start < 0 else old_list[block_start:next_item if next_item > 0 else len(old_list)]
        credit = re.search(r'<p class="credit">.*?</p>', block, re.S)
        credit = CREDITS.get(n, credit.group(0) if credit else "")
        pipe_start = block.find(f'<div class="panel" role="tabpanel" id="p-{n}-pipeline"')
        pipeline_panel = ""
        if n in NEW_PIPELINES:
            pipeline_panel = NEW_PIPELINES[n]()
        elif pipe_start >= 0:
            pipe_end = block.index("\n        </div>\n      </div></div>", pipe_start)
            pipeline_panel = block[pipe_start:pipe_end]
        repo_link = f"{base}{p['folder']}/README.md" if not publish else \
            base.replace("raw.githubusercontent.com", "github.com").replace("/main/", "/tree/main/") + p["folder"]
        items.append(project_html(p, base, credit, pipeline_panel, repo_link))

    after = end + len("</ul>")
    new_page = page[:start] + "\n" + "\n".join(items) + "\n  </ul>" + page[after:]
    new_page = new_page.replace("</head>", EXTRA_CSS, 1)
    #filter button for the undergraduate physics projects, and the right count before the script runs
    physics_btn = '\n    <button type="button" data-filter="physics" aria-pressed="false">physics</button>'
    if 'data-filter="physics"' not in new_page:
        markets_btn = '<button type="button" data-filter="markets" aria-pressed="false">markets</button>'
        new_page = new_page.replace(markets_btn, markets_btn + physics_btn, 1)
    new_page = re.sub(r'<span id="count">\d+ / \d+</span>', f'<span id="count">{len(PROJECTS)} / {len(PROJECTS)}</span>', new_page)
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
