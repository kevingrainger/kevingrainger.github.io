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
         summary=["A reef modelled like a magnet: healthy coral, bleached coral, bare rock and macroalgae on a lattice, nudged by heat and by neighbours. Reefs get stuck: once heat kills enough coral, cooling the water back does not bring it back. Mean-field models, where every patch feels every other, get stuck about 60% worse. Warming speed barely matters, and no early-warning signal fires before the slide.",
                  "Then a sharper question of real data: how much heat can Scott Reef's corals take? Driven by NOAA's degree heating weeks, with each colony given its own tolerance (a random-field Potts model), the reef is fitted by simulation-based inference to 65 AIMS surveys from April 2016. Two reefs fit equally well: one at NOAA's 4 DHW threshold, one tolerant to about 13 DHW. They disagree about February, and only an earlier survey could separate them. Run to destruction, the sensitive reef tips once the water holds 1.1-1.2 C above its warmest-month mean, the tolerant one at 1.4-1.7 C, and neither comes back."],
         stack="Python · Potts model · random-field disorder · Metropolis Monte Carlo · simulation-based inference · NumPy",
         hero=("figures/cover.gif", "The reef through a heatwave and back - and the path it takes"),
         steps=[("Give coral a way to die", "The original could never kill coral. Mortality under prolonged heat, and seaweed held back by grazers, make collapse possible.", "figures/fig2_reef_snapshots.png"),
                ("Warm, then cool", "Hysteresis loops at 4, 8 and 12 neighbours and mean field: the further the interaction reaches, the more stuck the reef gets.", "figures/hero.png"),
                ("Speed and warnings", "Speed of warming barely matters; peak heat does. Early-warning indicators stay silent through a gradual slide.", "figures/fig3_rate_map.png"),
                ("Use the field's heat measure", "Bleaching follows accumulated heat, not the day's temperature: NOAA's degree heating weeks over a rolling 12-week window. Colonies differ by 4-5 DHW in tolerance, so each patch gets its own threshold, smoothed in space.", "figures/fig8_scott_reef_2016.png"),
                ("Ask the surveys", "A mixture density network, written in NumPy and trained on 8,000 simulated reefs surveyed exactly as AIMS did, returns the posterior. 90% intervals hold the truth 90% of the time on held-out simulations. The real survey gives two modes: tolerance trades off against sensitivity.", "figures/fig9_tolerance.png"),
                ("Find the tipping point", "40 posterior draws, each warmed 0.1 C at a time and cooled back: the tipping temperature with error bars, and no recovery.", "figures/fig10_tipping_crw.png")],
         results=[("figures/hero.png", "Hysteresis against interaction range"), ("figures/fig8_scott_reef_2016.png", "Two reefs that fit the April 2016 surveys"),
                  ("figures/fig9_tolerance.png", "What the surveys say about coral tolerance"), ("figures/fig10_tipping_crw.png", "The tipping point with error bars"),
                  ("figures/fig3_rate_map.png", "Warming speed vs peak heat"), ("figures/fig4_early_warning.png", "No warning before a gradual collapse")]),
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
         summary=["What is the temperature between the weather stations? Daily maximum temperature on a 1 km grid: between stations the surface obeys a reduced heat-budget equation in which each land-cover class couples the air to the ground at its own rate; at stations it equals the reading exactly. XGBoost learns the heating the equation lacks and hands it back as a prior; a physics-informed U-Net, trained on stations with the heat budget in its loss, is the best model on heatwave days.",
                  "Validated on simulated daily fields with real station locations. The constraint holds to within a trillionth of a kelvin on every day. At held-out 50 km blocks the error falls from 1.34 K (ERA5-Land) to 0.79 K, level with regression-kriging at 0.85 K rather than clearly ahead of it. The physics turns out to be local, a few kilometres; the reach comes from the statistics. Real ERA5-Land, MODIS and station data next."],
         stack="Python · sparse PDE solver · adjoint gradients · variational anchoring · XGBoost · U-Net (JAX) · physics-informed loss · conformal prediction · folium",
         hero=("figures/cover.png", "Downscaled daily maximum temperature draped over the terrain, hottest July 2022 day (simulated test data)"),
         steps=[("Test the solver first", "A fake truth built from the PDE itself: planted parameters come back exactly when the physics is complete, within 25% when it is not.", "figures/fig0_step0_recovery.png"),
                ("Anchor the surface", "One adjoint solve per station gives its footprint; the smallest, smoothest forcing that makes the surface equal every station follows in closed form.", "figures/hero.png"),
                ("Hold out whole blocks", "Stations in 50 km blocks are left out together and scored in a year never used for fitting, against four baselines.", "figures/fig3_skill.png"),
                ("Read the missing physics", "The forcing the equation needed, averaged over all days, beside the land-cover map.", "figures/fig5_missing_physics.png"),
                ("Emulate the physics", "A 120,000-parameter U-Net in JAX learns the anchored surface from coarse fields alone, built per fold without that fold's stations. It matches the physics-only model overall (1.03 K) but smooths away the hottest days; conformalised, its 90% interval holds 86% of readings.", "figures/fig6_unet_surfaces.png"),
                ("Put the heat budget in the loss", "The same network trained on the thermometers, plus lambda times the squared residual of the solver's own stencil at every land cell. The physics costs a little at training stations and pays at unseen ones: on the hottest 5% of days the error falls from 1.12 K to 0.85 K, and anchored it is the best model on those days (0.75 K).", "figures/fig8_physics_informed.png")],
         results=[("figures/fig2_heatwave_day.png", "ERA5-Land, the anchored model and the hidden truth"), ("figures/fig3_skill.png", "Skill at held-out stations"),
                  ("figures/fig9_pinn_surfaces.png", "The heatwave day, data-only against physics-informed network"), ("figures/fig4_footprints.png", "Station footprints, calm and windy")],
         maps=[("maps/003-heatwave.html", "Interactive: the heatwave day at 1 km against ERA5-Land, with every station."),
               ("maps/003-unet-errors.html", "Interactive: error at every held-out station, physics against the U-Net emulator."),
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
    dict(num="007", tag="markets", tag_label="Markets", status="complete",
         folder="007-italian-power-volatility", title="Italian power price volatility",
         summary=["Three stages: what drives the Italian power price (XGBoost and SHAP, with gas taken out first), what drives its volatility (GARCH-MIDAS), and how much a weather forecast could add. Built and checked on simulated data with planted relationships, then run on real Italy North prices, Italian load and renewables, ERA5 temperature and TTF gas, 2018-2026.",
                  "On the real data the weather matters in the opposite direction to the published finding: months with more extreme days have calmer prices relative to gas, because in a heatwave gas plants set the price every hour. And even perfect knowledge of each month's extremes lowers the volatility forecast loss by only 0.7%, the ceiling on what a seasonal forecast could be worth."],
         stack="Python · XGBoost · SHAP · GARCH-MIDAS · QLIKE · Diebold-Mariano · Energy-Charts · ERA5",
         hero=("figures/fig5_real_price.png", "Italy North power and TTF gas, 2018-2026, with extreme-weather days per month"),
         steps=[("Weather to price", "Price relative to gas; XGBoost beats a straight line on unseen years and SHAP finds a U-shape in temperature.", "figures/fig6_real_shap.png"),
                ("Weather to volatility", "GARCH-MIDAS: the extreme-day count is significant, with a negative sign.", "figures/fig7_real_volatility.png"),
                ("Method check", "On simulated data the estimator recovers the planted weather effect on average.", "figures/fig3_midas_recovery.png")],
         results=[("figures/fig5_real_price.png", "Price, gas and extreme weather"), ("figures/fig6_real_shap.png", "What drives the price"),
                  ("figures/fig7_real_volatility.png", "Volatility components"), ("figures/fig3_midas_recovery.png", "Estimator check (simulated)")]),
    dict(num="008", tag="markets", tag_label="Markets", status="in progress",
         folder="008-spanish-solar-portfolio", title="Spanish solar portfolio strategy",
         summary=["How far does a cloud reach? An Anemoi ML-ready ERA5 dataset for Iberia, built with tested data-quality checks, CI and Docker, feeds a seasonal analysis of how correlated 25 Spanish solar sites are - the diversification a solar fleet really has.",
                  "On ERA5 2023 the weather stays correlated over 350-670 km, so 25 sites behave like 3-4. Then AI against physics: ECMWF's AIFS beats its physics model IFS for single sites from day 2, while for the fleet IFS leads for two days and AIFS from day 3 or 4. Forecast errors decorrelate over 170-230 km against the weather's 500, so pooling cancels them far better than it diversifies the weather. Next: CERRA, prices and cannibalisation."],
         stack="Python · anemoi-datasets · ERA5 · Zarr · AIFS · IFS · forecast verification · corrlib · CI/CD",
         hero=("figures/cover.png", "Correlation with Seville by season, and against distance for every site pair"),
         steps=[("Build the dataset", "ERA5 GRIB to an Anemoi Zarr dataset over Iberia, with quality checks written as tests.", "figures/fig1_two_weeks.png"),
                ("Measure the reach", "Correlation of clear-sky index against distance, by season.", "figures/fig2_correlation_vs_distance.png"),
                ("Remove the sun", "A daily shape every site shares, left by the clear-sky model, is subtracted before correlating.", "figures/fig0_daily_shape.png"),
                ("Month by month", "The same fit for each month of 2023.", "figures/fig3_monthly_reach.png"),
                ("Count independent sites", "Effective number of sites, raw and cleaned, by season.", "figures/fig4_effective_sites.png"),
                ("AI against physics", "AIFS and IFS daily solar forecasts, 1-7 days ahead, scored against ERA5 for each site and for the fleet.", "figures/fig5_forecast_skill.png"),
                ("Shared forecast errors", "Forecast errors against distance, beside the weather's own reach.", "figures/fig6_error_reach.png")],
         results=[("figures/hero.png", "The reach of the weather"), ("figures/fig2_correlation_vs_distance.png", "Correlation against distance"),
                  ("figures/fig4_effective_sites.png", "Effective sites by season"), ("figures/fig5_forecast_skill.png", "AIFS against IFS"),
                  ("figures/fig6_error_reach.png", "How far forecast errors reach"), ("figures/fig7_cloudy_week.png", "The worst miss")]),
    dict(num="012", tag="markets", tag_label="Markets", status="maths note",
         folder="012-percolation-tranche-loss", title="Ecology for bankers, revisited",
         summary=["In 2008 May, Levin and Sugihara asked what bankers could learn from ecologists. A 16-page LaTeX note derives their tools: May's stability bound from the circular law, percolation thresholds on random networks, and the effect of disassortative wiring, which doubles the threshold for the same degree sequence but fails most completely once crossed.",
                  "Two case studies. The Rhine low water of 2018, rerun on 4,000 firms at the real Rhine-basin centres and calibrated to a 1% monthly loss of German output: the same 1% fits economies anywhere from 6% to 89% of the way to their threshold, and what tips the next one is road and rail, not the river. Structured credit: at the same mean loss as Vasicek, the 15-30% tranche carries 46 times the expected loss."],
         stack="Python · random matrices · percolation · generating functions · directed networks · folium · LaTeX",
         hero=("figures/fig4_rhine_map.png", "The Rhine at its 25 cm record: the network as calibrated to 2018, and with road and rail strained past the threshold"),
         steps=[("May's bound", "Community-matrix eigenvalues fill a disc of radius σ√(NC); stability is lost sharply at 1.", "figures/fig1_may_stability.png"),
                ("Percolation", "The giant failure cluster appears at T = <k>/(<k²> - <k>).", "figures/fig2_percolation_surface.png"),
                ("Disassortative wiring", "Same degrees, rewired: the threshold doubles, then the order reverses.", "figures/fig3_disassortativity.png"),
                ("The Rhine runs dry", "One aggregate number fixes a line of possible economies, not a point.", "figures/fig5_rhine_futures.png"),
                ("Structured credit", "At equal mean loss, risk moves up the capital structure.", "figures/fig7_equal_mean.png")],
         results=[("figures/fig5_rhine_futures.png", "Three economies that all match 2018"), ("figures/fig7_equal_mean.png", "Equal mean, different tails"),
                  ("figures/fig3_disassortativity.png", "Same degrees, different wiring"), ("figures/fig6_tranche_switch.png", "The senior tranche switches on")],
         maps=[("maps/012-rhine-cascade.html", "Interactive: disruption probability for every firm at Kaub 25 cm, as calibrated and with substitution strained.")]),
    dict(num="013", tag="markets", tag_label="Markets", status="complete",
         folder="013-coffee-forward-curves", title="Coffee, frost and the forward curve",
         summary=["In July 2021 frost hit Brazil's coffee belt and arabica rose by a third in a week. When a forecast warns of frost, does the price move with the warning or with the damage, and how far along the forward curve does it reach? A production-weighted frost index is built from ERA5 and from archived ECMWF and GFS forecasts, by lead time.",
                  "The market read the forecasts promptly: across 2021-2026 no reaction comes a day or two late, as Roll found for orange juice. But the largest move followed the frost night, once the damage was known. A Schwartz two-factor model fitted to the 2024-2026 curves puts the half-life of a convenience-yield shock at about three years."],
         stack="Python · Kalman filter · Schwartz two-factor model · event study · Newey-West · ECMWF and GFS forecast archive",
         hero=("figures/fig1_frost_2021.png", "July 2021: frost warnings in the forecasts, frost nights in ERA5, and the price of arabica"),
         steps=[("A frost index", "Production-weighted cold below 5 C at eight regions, from ERA5 and from forecasts issued 1-7 days ahead.", "figures/fig1_frost_2021.png"),
                ("Line up the events", "Price paths around every frost night since 2000 and every first warning since 2021.", "figures/fig2_events.png"),
                ("Read the curve", "Schwartz's model by Kalman filter: how far a convenience-yield shock reaches, and its path since 2024.", "figures/fig3_curve.png")],
         results=[("figures/fig1_frost_2021.png", "July 2021"), ("figures/fig2_events.png", "Event study"),
                  ("figures/fig3_curve.png", "The forward curve")]),
    dict(num="014", tag="markets", tag_label="Markets", status="complete",
         folder="014-copper-satellite-signals", title="Copper seen from space",
         summary=["Copper's supply chain is short and visible: concentrate leaves a handful of Chilean and Peruvian ports, and smelters glow in shortwave infrared. Ship traffic comes from IMF PortWatch (AIS), and furnaces are located with a Sentinel-2 hot-spot test. Placebo ports that ship forestry, salmon and fishmeal are a check.",
                  "The ships see copper: Peru's copper ports track official copper exports (r = 0.67, against 0.27 for the placebos), and Grasberg's port went quiet after the September 2025 mudslide (-89%). Smelter heat, from 9,900 Sentinel-2 passes at 24 sites since 2019, is steady where it should be. But neither ships nor heat predict the copper price a month ahead out of sample: the supply is visible, and already in the price."],
         stack="Python · IMF PortWatch (AIS) · Sentinel-2 · Earth Engine · rasterio · out-of-sample testing",
         hero=("figures/fig3_smelters.png", "Four copper smelters in Sentinel-2 shortwave infrared, hot pixels outlined"),
         steps=[("Watch the ports", "Daily dry-bulk exports at 11 copper ports, Grasberg's port and 7 placebos.", "figures/fig1_validation.png"),
                ("Check against truth", "Peru's central bank publishes monthly copper export volumes; the copper ports follow them, the placebos do not.", "figures/fig1_validation.png"),
                ("A real shock", "Amamapare before and after the Grasberg mudslide.", "figures/fig2_grasberg.png"),
                ("Find the furnaces", "A shortwave-infrared hot-spot test locates 24 of 30 smelters; a closed plant kept as a check shows its limits.", "figures/fig3_smelters.png"),
                ("Watch them run", "Hot pixels by month at each smelter, 2019-2026, compared year on year.", "figures/fig4_smelter_heat.png")],
         results=[("figures/fig1_validation.png", "Ships against official exports"), ("figures/fig2_grasberg.png", "Grasberg, September 2025"),
                  ("figures/fig3_smelters.png", "Smelters in shortwave infrared"), ("figures/fig4_smelter_heat.png", "Smelter heat over time")]),
    dict(num="015", tag="markets", tag_label="Markets", status="complete",
         folder="015-commodity-option-hedging", title="Hedging commodity options through a shock",
         summary=["Sell a 3-month option on copper, gold, wheat, corn, coffee or cocoa futures every month since 2002 and hedge it eight ways: static, weekly, on 2% moves, daily, daily with GARCH volatility, Leland's cost adjustment and the Whalley-Wilmott band.",
                  "In calm markets daily hedging tracks best and the band comes within a point at three-quarters of the cost. In a shock every dynamic hedge lands within two points of the others: the loss is set by the volatility the option was sold at, error/premium ≈ -½ × variance surprise, and simulations pin the damage on wandering volatility rather than jumps."],
         stack="Python · Black-76 · GARCH · Whalley-Wilmott · Leland · Merton and Heston Monte Carlo",
         hero=("figures/fig2_copper_2025.png", "A copper call sold on 1 July 2025, hedged four ways through the tariff jump and the exemption crash"),
         steps=[("Sell and hedge", "1,738 three-month trades across six commodities, eight strategies, 5 bp trading cost.", "figures/fig2_copper_2025.png"),
                ("Calm against shock", "Tracking error against trading cost, split by whether volatility surprised.", "figures/fig1_frontier.png"),
                ("Why shocks hurt", "Every trade's error against its variance surprise, beside the one-line theory.", "figures/fig3_variance_surprise.png"),
                ("What breaks which hedge", "The same trades in four simulated markets: constant volatility, jumps, wandering volatility, a scheduled jump.", "figures/fig4_monte_carlo.png")],
         results=[("figures/fig1_frontier.png", "Error against cost"), ("figures/fig3_variance_surprise.png", "The variance surprise"),
                  ("figures/fig4_monte_carlo.png", "Simulated markets"), ("figures/fig2_copper_2025.png", "Copper, summer 2025")]),
    dict(num="016", tag="earth", tag_label="Earth systems", status="complete",
         folder="016-sahel-desertification", title="Desertification in the Sahel",
         summary=["Plants that help plants: the Kéfi lattice, in which bare soil recovers faster next to vegetation, the same neighbour coupling as the coral reef's Potts model. With strong facilitation the way back from desert is longer than the way down, and the mean-field theory overstates the trap.",
                  "The vegetation stops connecting long before it disappears: the largest patch falls from 90% of all vegetation to 6% while cover is still near a half, well before the collapse. A satellite counting patch sizes would see the warning. Driven by real rainfall at Gourma and Fakara, the model shows that rain alone cannot explain which site re-greened: at Fakara, greenness has stopped following the rain, and land use decides."],
         stack="Python · Numba cellular automaton · pair approximation · percolation · Sentinel-2 · MODIS",
         hero=("figures/fig1_hysteresis.png", "Vegetation cover as rainfall falls and rises again, for three strengths of facilitation"),
         steps=[("Plants that help plants", "A three-state lattice; facilitation f couples each cell to its neighbours.", "figures/fig1_hysteresis.png"),
                ("Theory against simulation", "Mean field and pair approximation beside the lattice.", "figures/fig2_theory.png"),
                ("The warning from above", "The largest patch's share collapses before cover does; large patches vanish first.", "figures/fig3_early_warning.png"),
                ("Real patterns", "Sentinel-2 NDVI at Gourma and Fakara beside the model lattice.", "figures/fig4_patterns.png"),
                ("Real rain, real greenness", "The lattice driven by 1950-2025 rainfall, against MODIS greenness from 2000.", "figures/fig5_sites.png")],
         results=[("figures/fig1_hysteresis.png", "Hysteresis"), ("figures/fig2_theory.png", "Theory against simulation"),
                  ("figures/fig3_early_warning.png", "Early warning"), ("figures/fig5_sites.png", "Two sites")]),
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
    '001': '<p class="credit"><sup>&dagger;</sup>Builds on Mumby, Hastings &amp; Edwards (2007). Heat stress from NOAA Coral Reef Watch (<a href="https://doi.org/10.3390/rs12233856">Skirving et al. 2020</a>); surveys from the Global Coral Bleaching Database (<a href="https://doi.org/10.1038/s41597-022-01121-y">van Woesik &amp; Kratochwill 2022</a>), collected by the Australian Institute of Marine Science. Tolerance variation after Humanes et al. (2022). Inference after <a href="https://doi.org/10.1073/pnas.1912789117">Cranmer, Brehmer &amp; Louppe (2020)</a> and Papamakarios &amp; Murray (2016).</p>',
    '002': '<p class="credit"><sup>&dagger;</sup>Recreation of <a href="https://doi.org/10.1038/s41598-019-44997-4">Fierro, Liccardo &amp; Porcelli (2019)</a>, <em>Scientific Reports</em>.</p>',
    '003': '<p class="credit"><sup>&dagger;</sup>Variational analysis from Sasaki (1970) and Lorenc (1986). Positioned against E-OBS (<a href="https://doi.org/10.1029/2017JD028200">Cornes et al. 2018</a>) and ERA5-Land (<a href="https://doi.org/10.5194/essd-13-4349-2021">Mu&ntilde;oz-Sabater et al. 2021</a>); closest published relative <a href="https://doi.org/10.3390/cli10030047">Wilson et al. (2022)</a>, First Street Foundation. XGBoost from Chen &amp; Guestrin (2016). Physics-informed networks after <a href="https://doi.org/10.1016/j.jcp.2018.10.045">Raissi, Perdikaris &amp; Karniadakis (2019)</a>. Station list from Meteostat.</p>',
    '004': '<p class="credit"><sup>&dagger;</sup>Builds on Epps (1979), Laloux, Cizeau, Bouchaud &amp; Potters (1999), Ledoit &amp; Wolf (2004, 2020) and Capon (1969). Prices from Yahoo Finance via yfinance.</p>',
    '005': '<p class="credit"><sup>&dagger;</sup>STA/LTA from Allen (1978); optimal array weights from Capon (1969). Labelled waveforms from <a href="https://doi.org/10.1029/2017JB015251">Ross, Meier &amp; Hauksson (2018)</a>, Southern California Seismic Network data via the <a href="https://doi.org/10.7909/C3WD3xH1">SCEDC</a>.</p>',
    '006': '<p class="credit"><sup>&dagger;</sup>Control variate from Kemna &amp; Vorst (1990). Projected SOR as in Wilmott, Howison &amp; Dewynne (1995). Prices from Yahoo Finance via yfinance; SET50 history from Investing.com.</p>',
    '009': '<p class="credit"><sup>&dagger;</sup>Projected SOR as in Wilmott, Howison &amp; Dewynne (1995).</p>',
    '010': '<p class="credit"><sup>&dagger;</sup>Exact critical point from Baxter (1973); Metropolis et al. (1953).</p>',
    '011': '',
    '012': '<p class="credit"><sup>&dagger;</sup>Builds on <a href="https://doi.org/10.1038/451893a">May, Levin &amp; Sugihara (2008)</a>, May (1972), Newman, Strogatz &amp; Watts (2001), Watts (2002), Gai &amp; Kapadia (2010) and Vasicek (2002). Low-water effect from <a href="https://doi.org/10.1515/ger-2022-0077">Ademmer, Jannsen &amp; Meuchelb&ouml;ck (2023)</a>. Basemap: Natural Earth.</p>',
    '013': '<p class="credit"><sup>&dagger;</sup>Builds on Roll (1984) and Schwartz (1997). Forecasts from ECMWF IFS and NOAA GFS via the Open-Meteo archive; ERA5 (<a href="https://doi.org/10.1002/qj.3803">Hersbach et al. 2020</a>). Prices from Yahoo Finance.</p>',
    '014': '<p class="credit"><sup>&dagger;</sup>Ship data from <a href="https://portwatch.imf.org">IMF PortWatch</a> (Arslanalp, Koepke &amp; Verschuur 2021); official exports from the Banco Central de Reserva del Per&uacute;. Hot-spot test after Murphy et al. (2016). Contains modified Copernicus Sentinel-2 data, via Microsoft Planetary Computer.</p>',
    '015': '<p class="credit"><sup>&dagger;</sup>Builds on Black (1976), Leland (1985), Whalley &amp; Wilmott (1997), Hull &amp; White (2017), Merton (1976), Heston (1993) and Bollerslev (1986). Prices from Yahoo Finance.</p>',
    '016': '<p class="credit"><sup>&dagger;</sup>Builds on K&eacute;fi et al. (2007), Rietkerk et al. (2004) and Scanlon et al. (2007). Sites after Dardel et al. (2014). Contains modified Copernicus Sentinel-2 data; MODIS NDVI via the ORNL DAAC; ERA5 rainfall via Open-Meteo.</p>',
    '007': '<p class="credit"><sup>&dagger;</sup>Builds on Guerzoni, Riso &amp; Zoia (2026). GARCH-MIDAS from Engle, Ghysels &amp; Sohn (2013).</p>',
    '008': '<p class="credit"><sup>&dagger;</sup>Weather from ERA5 (<a href="https://doi.org/10.1002/qj.3803">Hersbach et al. 2020</a>), built with ECMWF\'s anemoi-datasets. Contains modified Copernicus Climate Change Service information (2023). Capture-rate framing from Hirth (2013).</p>',
}

# Pipeline-tab notes written before the code existed, brought up to date
PIPELINE_FIXES = [
    ("<b>Output (planned).</b>", "<b>Output.</b>"),
    ('<p class="flow-note">Steps 1–2 are the code in the repo now; steps 3–4 are the planned scoreboard.</p>', ""),
    ('<p class="flow-note">Planned structure; Asian pricing and the SET50 calibration are still being built.</p>', ""),
    ('<p class="flow-note">Planned structure.</p><ol class="flow"><li><b>Input.</b> GME',
     '<p class="flow-note">The plan for real data; the code currently runs on simulated data of the same shape.</p><ol class="flow"><li><b>Input.</b> GME'),
    ("the code currently runs on a placeholder of the same shape.", "the code currently runs on simulated data of the same shape."),
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
    "001": lambda: draw_pipeline(
        "001", "Coral reef: lattice model, real heat stress and inference",
        ["Inputs", "Model", "Experiments", "Inference", "Outputs"],
        [("dhw", "NOAA heat stress", "DHW, Scott-Ashmore", 0, 0, "input"), ("aims", "AIMS surveys", "65 sites, April 2016", 0, 3, "input"),
         ("potts", "Potts lattice", "four states, Metropolis", 1, 0, "step"), ("tol", "Colony tolerance", "random field D50", 1, 1, "step"),
         ("hyst", "Hysteresis sweeps", "mean field vs lattice", 2, 0, "step"), ("ews", "Early warnings", "variance, AR(1)", 2, 1, "step"),
         ("bank", "Simulation bank", "8,000 reefs", 2, 2, "step"), ("mdn", "Density network", "NumPy, calibrated", 3, 3, "step"),
         ("tip", "Tipping point", "with error bars", 4, 0, "output"), ("post", "Two reefs", "4.5 vs 12.7 DHW", 4, 1, "output")],
        [("dhw", "potts", True), ("tol", "potts", True), ("potts", "hyst", True), ("potts", "ews", False), ("tol", "bank", True),
         ("bank", "mdn", True), ("aims", "mdn", True), ("mdn", "post", True), ("post", "tip", True), ("hyst", "tip", True)],
        "The first version used a temperature curve; this one runs on NOAA's heat stress and is fitted to real surveys.",
        [("Inputs", "NOAA Coral Reef Watch degree heating weeks for the Scott-Ashmore station, and 65 AIMS bleaching surveys of Scott Reef in April 2016."),
         ("Model", "A Potts lattice of healthy, bleached and dead coral and macroalgae, in which each patch has its own heat tolerance."),
         ("Experiments", "Warming and cooling sweeps for hysteresis, and early-warning statistics."),
         ("Inference", "8,000 simulated reefs train a NumPy mixture density network that returns the posterior from one survey."),
         ("Output", "Two reefs that fit equally well, and the tipping temperature for each with error bars.")]),
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
         ("q", "Missing physics", "mean q map", 4, 2, "output"),
         ("pinn", "Physics-informed", "U-Net + PDE residual", 3, 3, "step"),
         ("hot", "Hottest days", "0.75 K, anchored", 4, 3, "output")],
        [("era", "red", True), ("lst", "gap", True), ("static", "taus", True), ("red", "gap", False), ("red", "fit", False),
         ("gap", "pde", True), ("taus", "pde", False), ("fit", "pde", False), ("pde", "anc", True), ("st", "anc", True),
         ("anc", "xgb", True), ("st", "cv", False), ("anc", "tmax", True), ("xgb", "q", True),
         ("pde", "pinn", True), ("pinn", "hot", True)],
        "The code runs end to end on simulated daily fields of the same shape; the download script for the real products ships with it.",
        [("Input", "ERA5-Land daily maximum temperature, skin temperature and afternoon wind at 0.1°; MODIS Aqua daytime land surface temperature at 1 km; elevation and six land-cover fractions per 1 km cell; station daily maxima."),
         ("Daily fields", "Everything is reduced to sea level with a 6.5 K/km lapse rate. Cloud gaps in the MODIS field are filled with ERA5-Land skin temperature plus each cell's mean clear-sky offset for the month."),
         ("Physics", "A steady advection-diffusion-relaxation equation is assembled as a sparse system and factorised once per day. Its relaxation times, one per land-cover class, are fitted with adjoint gradients."),
         ("Anchor and learn", "One adjoint solve per station gives its footprint. The smallest, smoothest forcing q that makes the surface equal every station is found in closed form; XGBoost learns q from land cover and terrain and supplies it as a prior."),
         ("Learn", "A U-Net emulates the anchored surface with conformal intervals; a physics-informed U-Net is trained on station readings with the heat-budget residual in its loss."),
         ("Output", "Daily maximum temperature at 1 km that returns every station reading exactly, a map of the heating the equation lacks, and a skill table from 50 km blocks held out in a year never used for fitting.")]),
    "012": lambda: draw_pipeline(
        "012", "Ecology for bankers: theory and two case studies",
        ["Theory", "Thresholds", "Network", "Calibrate", "Outputs"],
        [("may", "May's bound", "circular law", 0, 0, "input"), ("perc", "Percolation", "generating functions", 0, 1, "input"),
         ("corr", "Degree correlations", "rewiring", 0, 2, "input"),
         ("tc", "Threshold T_c", "leading eigenvalue", 1, 1, "step"),
         ("rhine", "Rhine firms", "20 real centres", 2, 0, "step"), ("pool", "Credit pool", "Poisson network", 2, 2, "step"),
         ("kaub", "Kaub 2018", "1% output, 30 days", 3, 0, "input"), ("vas", "Vasicek", "equal mean loss", 3, 2, "input"),
         ("line", "Calibration line", "T*/T_c vs direct share", 4, 0, "output"), ("tr", "Tranche losses", "risk moves up", 4, 2, "output")],
        [("may", "tc", False), ("perc", "tc", True), ("corr", "tc", True), ("tc", "rhine", True), ("tc", "pool", True),
         ("rhine", "kaub", True), ("kaub", "line", True), ("pool", "vas", True), ("vas", "tr", True)],
        "Theory first, each result checked by simulation on networks of 10,000 nodes; the two case studies reuse the same threshold.",
        [("Theory", "May's bound from the eigenvalues of a random community matrix; percolation thresholds from generating functions; the correlated threshold from the matrix (k'-1)P(k'|k)."),
         ("Network", "4,000 firms at real Rhine-basin centres, suppliers chosen by sector and distance; and a credit pool on a Poisson network."),
         ("Calibrate", "Transmissibility by bisection so a low-water month costs 1% of German output; the credit model matched to a Vasicek mean loss."),
         ("Output", "The line of economies consistent with 2018 and their distance to the threshold; expected loss by tranche.")]),
    "013": lambda: draw_pipeline(
        "013", "Coffee: frost forecasts and the forward curve",
        ["Inputs", "Indices", "Events and curve", "Timing", "Outputs"],
        [("era", "ERA5", "8 regions, 1990-", 0, 0, "input"), ("fc", "GFS and ECMWF", "forecasts by lead", 0, 1, "input"),
         ("kc", "ICE arabica", "front and contracts", 0, 2, "input"),
         ("frost", "Frost nights", "cold below 5 C", 1, 0, "step"), ("warn", "Frost warnings", "max over 7 days", 1, 1, "step"),
         ("ev", "Event study", "price around events", 2, 0, "step"), ("kal", "Schwartz model", "Kalman filter", 2, 2, "step"),
         ("nw", "Timing test", "Newey-West", 3, 1, "step"),
         ("when", "When it is priced", "with the damage", 4, 0, "output"), ("reach", "Curve reach", "half-life 3 years", 4, 2, "output")],
        [("era", "frost", True), ("fc", "warn", True), ("frost", "ev", True), ("warn", "ev", True), ("warn", "nw", True),
         ("kc", "kal", True), ("warn", "kal", False), ("ev", "when", True), ("nw", "when", True), ("kal", "reach", True)],
        "Free data only: archived forecasts by lead time from Open-Meteo, futures from Yahoo Finance.",
        [("Inputs", "ERA5 minimum temperature at eight coffee regions, GFS and ECMWF forecasts 1-7 days ahead, and ICE arabica futures."),
         ("Indices", "A production-weighted cold excess below 5 C, and the largest one forecast for the coming week."),
         ("Tests", "Price paths around each event, and whether a new warning is priced the same day."),
         ("Curve", "The Schwartz two-factor model by Kalman filter, with the warning in the convenience yield."),
         ("Output", "When the market prices a frost, and how far along the curve the shock reaches.")]),
    "014": lambda: draw_pipeline(
        "014", "Copper from space: ships and smelter heat",
        ["Inputs", "Locate", "Measure", "Test", "Outputs"],
        [("ais", "IMF PortWatch", "AIS port calls", 0, 0, "input"), ("s2", "Sentinel-2", "SWIR, 2019-", 0, 1, "input"),
         ("ships", "Copper ports", "dry-bulk tonnes", 1, 0, "step"), ("loc", "Find furnaces", "hot-spot test", 1, 1, "step"),
         ("bcrp", "Peru exports", "BCRP official", 1, 2, "input"),
         ("val", "Validation", "vs official, placebos", 2, 0, "step"), ("heat", "Smelter heat", "24 sites, every pass", 2, 1, "step"),
         ("oos", "Out of sample", "next-month copper", 3, 1, "step"),
         ("seen", "Supply is visible", "r = 0.67, Grasberg", 4, 0, "output"), ("priced", "Already priced", "no skill", 4, 1, "output")],
        [("ais", "ships", True), ("s2", "loc", True), ("loc", "heat", True), ("ships", "val", True), ("bcrp", "val", True),
         ("val", "seen", True), ("val", "oos", True), ("heat", "oos", True), ("oos", "priced", True)],
        "Every source is free and needs no account; an Earth Engine version of the heat series runs closer to live.",
        [("Inputs", "Daily port calls and cargo from IMF PortWatch, Sentinel-2 shortwave infrared, and official Peruvian copper exports."),
         ("Signals", "Dry-bulk exports at 11 copper ports, and hot-pixel counts at 24 smelters on every clear pass."),
         ("Checks", "Ships against official exports, with placebo ports; furnaces located on imagery, with a closed plant as a control."),
         ("Test", "Expanding-window regressions of the next month's copper price on each signal."),
         ("Output", "The supply can be seen, and it is already in the price.")]),
    "015": lambda: draw_pipeline(
        "015", "Hedging commodity options through a shock",
        ["Inputs", "Pricing", "Hedges", "Scoring", "Outputs"],
        [("fut", "Six futures", "metals, grains, softs", 0, 0, "input"), ("sim", "Simulated markets", "GBM, Merton, Heston", 0, 2, "input"),
         ("vol", "Volatility", "realised, GARCH", 1, 0, "step"), ("blk", "Black-76", "price and delta", 1, 1, "step"),
         ("hedge", "Eight hedges", "static to band", 2, 1, "step"),
         ("calm", "Calm trades", "error vs cost", 3, 0, "step"), ("shock", "Shock trades", "vol surprised", 3, 1, "step"),
         ("mc", "Monte Carlo", "2,000 paths each", 3, 2, "step"),
         ("front", "Frontier", "band near daily", 4, 0, "output"), ("why", "Why shocks hurt", "-1/2 variance surprise", 4, 1, "output")],
        [("fut", "vol", True), ("vol", "blk", True), ("blk", "hedge", True), ("hedge", "calm", True), ("hedge", "shock", True),
         ("sim", "mc", True), ("hedge", "mc", False), ("calm", "front", True), ("shock", "why", True), ("mc", "why", False)],
        "1,738 real trades from 2002, and the same hedges in four simulated markets.",
        [("Inputs", "Front-month futures for copper, gold, wheat, corn, coffee and cocoa."),
         ("Pricing", "Black-76 at trailing realised volatility, or a GARCH forecast."),
         ("Hedges", "Static, weekly, on 2% moves, daily, GARCH, Leland and the Whalley-Wilmott band, at 5 bp a trade."),
         ("Scoring", "Error and cost as a share of the premium, split by whether volatility surprised."),
         ("Output", "The cost-tracking frontier, and the variance-surprise law that sets shock losses.")]),
    "016": lambda: draw_pipeline(
        "016", "Sahel: facilitation, tipping and early warning",
        ["Theory", "Model", "Signals", "Real sites", "Outputs"],
        [("mf", "Mean field", "no space", 0, 0, "input"), ("pa", "Pair approximation", "neighbour pairs", 0, 1, "input"),
         ("ca", "Kefi lattice", "plants help plants", 1, 1, "step"),
         ("hy", "Hysteresis", "drying and wetting", 2, 0, "step"), ("ps", "Patch sizes", "percolation", 2, 1, "step"),
         ("rain", "ERA5 rainfall", "1950-2025", 3, 2, "input"), ("ndvi", "MODIS, Sentinel-2", "greenness, patches", 3, 3, "input"),
         ("trap", "The trap", "space shrinks it", 4, 0, "output"), ("warn", "Early warning", "network breaks first", 4, 1, "output"),
         ("land", "Two sites", "rain is not enough", 4, 2, "output")],
        [("mf", "hy", False), ("pa", "ca", False), ("ca", "hy", True), ("ca", "ps", True), ("hy", "trap", True),
         ("ps", "warn", True), ("rain", "land", True), ("ndvi", "land", True)],
        "The last project of the portfolio: the coral model's maths on land.",
        [("Theory", "Mean-field and pair-approximation equations for the three-state model."),
         ("Model", "A Numba lattice of vegetated, empty and degraded cells, with facilitation f."),
         ("Signals", "Hysteresis loops, and patch sizes and spanning clusters as the landscape dries."),
         ("Real sites", "Gourma and Fakara: ERA5 rain drives the lattice, MODIS and Sentinel-2 check it."),
         ("Output", "How far theory overstates the trap, an early warning visible from space, and why rain alone cannot explain which site re-greened.")]),
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
