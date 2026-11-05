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
    dict(num="001", key="000", tag="physics", tag_label="Physics", status="capstone",
         folder="earlier-work/dft-porphyrin-networks", title="DFT simulations of metal-porphyrin 2D nano-networks",
         summary=["My undergraduate capstone at Trinity College Dublin, supervised by Prof. Cormac McGuinness: an attempt to model the electronic shell structure and spin patterns of metal-porphyrin nano-networks with density functional theory. Porphyrins are flat rings of four pyrroles that hold a metal atom at the centre. They are the core of haemoglobin (iron) and chlorophyll (magnesium), and their spin and charge can be tuned through the central metal and whatever binds to it, which makes them candidates for molecular electronics, catalysis and chemical sensing. On-surface synthesis can now fuse them into chains and ribbons, and the project carries on from earlier studies of these larger porphyrin systems. The calculations ran in FHI-aims, the Fritz Haber Institute's density functional theory code, which expands the electron orbitals in numeric atom-centred functions. DFT replaces the many-electron wavefunction with the electron density and solves the Kohn-Sham equations self-consistently.",
                  "The main focus was how the bridge between units (weak, strong or fully fused), the central metal and the fused ligand arms combine to set the spin and the energy gap. The metals were zinc, iron, vanadium, cobalt and manganese, chosen to span the d shell from three electrons to ten. The bridge decides whether a bare chain is magnetic: weakly joined chains grow unpaired electrons on their carbon backbone, while fully fused ones pair them up. The metal matters through its d electrons: zinc's full shell leaves the carbon backbone on its own, while vanadium and iron put their d orbitals at the frontier. One oxygen bound to the metal overrides the bridge: every iron chain settles at S = 1 and every vanadium chain at S = ½, with the backbone spin gone and the gap still set by the bridge. A spin that switches when a molecule binds is the mechanism a chemical sensor needs."],
         stack="FHI-aims · spin-polarised DFT · Kohn-Sham · Mulliken analysis · Python · matplotlib",
         hero=("figures/cover_znextra_homo.png", "The highest occupied orbital of the extra-strongly fused zinc chain"),
         steps=[("Start from one molecule", "Plain porphyrin, then four and two fused arms. The two-arm molecule's gap collapses, the sign of two unpaired electrons.", "figures/fig4_zinc_molecule_orbitals.png"),
                ("Give the molecule a magnetic metal", "Iron, manganese, cobalt and vanadium: two fused arms add about 2 μB on the ring aligned with the metal, as measured for iron on gold.", "figures/fig10_molecule_spin_by_metal.png"),
                ("Join them into chains", "Weak, strong and extra-strong bridges. Only the fully fused backbone carries its HOMO the whole length of the chain.", "figures/fig3_zinc_chain_orbitals.png"),
                ("Put the metal in the chain", "In the vanadium and iron chains the metal's d orbital sits at the frontier.", "figures/fig6_vanadium_chain_orbitals.png"),
                ("Bind an oxygen to the metal", "Bare chains disagree about where the spin sits; with Fe=O or V=O every chain lands in the same local spin state.", "figures/fig8_oxo_spin_by_element.png"),
                ("See why", "The metal's states move away from the chemical potential, leaving the spin on the metal-oxo unit and the conduction in the carbon bands.", "figures/fig9_oxo_spin_dos.png"),
                ("All the design variables together", "Metal and arms set the ring's spin; the bridge sets the bare backbone's; one oxygen removes it everywhere while the bridge still sets the gap.", "figures/fig11_covariates.png")],
         results=[("figures/fig11_covariates.png", "Metal, arms, bridge and oxygen against spin and gap"),
                  ("figures/fig8_oxo_spin_by_element.png", "Where the spin sits, bare and with O on the metal"),
                  ("figures/fig9_oxo_spin_dos.png", "Spin-resolved density of states"),
                  ("figures/fig10_molecule_spin_by_metal.png", "Spin on the metal and the ring, four metals"),
                  ("figures/fig7_feo_ribbon_orbitals.png", "An Fe=O porphyrin in a graphene nanoribbon"),
                  ("figures/fig1_molecule_gaps.png", "Single-molecule gaps")]),
    dict(num="002", key="002", tag="earth", tag_label="Earth systems", status="complete",
         folder="002-olive-grove-xylella", title="Olive grove Xylella, stochastic SIR",
         summary=["A rebuilt agent-based model of Xylella spreading through an olive grove, carried from tree to tree by spittlebugs. I implemented a lighter version of the original model, checked against it, so that it can be run and tuned many more times. Outbreaks are usually fatal: 39 of 40 take the whole grove, half of it within about 2.3 years. I expected some kind of equilibrium, with dying trees slowing the spread, but none appeared: a tree takes about two years to show symptoms, which leaves plenty of time for the bacterium to reach the trees around it. A natural next step is multilevel Monte Carlo: most runs on a cheap, coarse version of the grove, and a few on progressively finer versions to correct what the coarsening gets wrong, so the full model is only paid for where it changes the answer.",
                  "The aim was to bring in percolation theory and look for planting spacings and felling patterns that break up the spread. Two thresholds turned up. A spittlebug stays on a tree for about 18 days at a time. If its chance of passing on the infection during that stay is below roughly 16%, outbreaks die out; above about 29%, they take the grove. Spacing acts like a percolation threshold too: with the number of spittlebugs per tree held fixed, outbreaks stop taking the grove once trees are 6 to 8 cells apart. Many felling patterns were tried, varying the radius and how quickly infected trees are found, and none slowed the spread. A first twin experiment with a particle filter shows what data assimilation needs: counting dead trees from above leaves the infection rate almost unconstrained (anywhere from 0.1 to 0.9 after six years), because every outbreak above the threshold takes the whole grove. The images have to show which trees die and in what order. The next step is to fit that spatial pattern in real image sequences, like the Gallipoli pair, with a Wasserstein-distance loss and multilevel Monte Carlo to keep the runs affordable, before designing felling patterns."],
         stack="Python · agent-based modelling · ensembles · percolation threshold",
         hero=("figures/hero_no_control.png", "Five years after one infected spittlebug arrives, with no control"),
         steps=[("Rebuild, lighter", "The same rules applied to every spittlebug at once, so many more runs fit in the same time; statistically identical to the original over 12 + 200 runs.", "figures/fig1_grove_day1095.png"),
                ("Find the bug that mattered", "A wrong season on day 0 gave every outbreak a head start: 38% more infection by day 600.", "figures/fig2_ensemble.png"),
                ("Find the threshold", "A visit lasts about 18 days; outbreaks die out below roughly 16-29% infection per visit and take the grove above it.", "figures/fig3_threshold.png"),
                ("Test felling", "Radius x detection speed on a 1,156-tree grove: felling removes trees faster than it stops the disease.", "figures/fig6_felling_grid.png"),
                ("Planting spacing", "Spreading the trees apart, with spittlebugs per tree held fixed: outbreaks stop taking the grove between 6 and 8 cells apart.", "figures/fig_spacing_threshold.png"),
                ("Assimilate the images", "A particle filter on satellite-like counts can't pin the infection rate down: the spread pattern is what carries it.", "figures/fig8_assimilation.png"),
                ("A real grove", "A grove near Gallipoli of about the simulated size: full canopies in 2014, gone by 2026. The kind of image sequence data assimilation would fit the model to.", "figures/fig_real_grove.png")],
         results=[("figures/fig_real_grove.png", "A real grove near Gallipoli, 2014 and 2026"), ("figures/fig0_animation.gif", "Three years in twenty seconds"),
                  ("figures/fig_spacing_threshold.png", "Planting further apart"), ("figures/fig3_threshold.png", "All-or-nothing threshold"), ("figures/fig6_felling_grid.png", "Felling grid")]),
    dict(num="003", key="001", tag="earth", tag_label="Earth systems", status="complete",
         folder="001-coral-reef-tipping-points", title="Coral reef tipping points",
         summary=["This project models a reef much as physics models a magnet. Taking the Potts and Ising models as inspiration, it treats the reef as a lattice of interacting cells, a variation on cellular automata. Each square is healthy coral, bleached coral, bare rock or seaweed. Its interactions with its nearest and second-nearest neighbours are set to approximate real biological processes: coral spreading into free space nearby, grazing fish keeping seaweed down, and coral dying under prolonged heat. The results were mixed. Reefs get stuck: once heat kills enough coral, cooling the water back down does not bring it back. A mean-field model, where every patch feels every other, gets stuck about 60% worse than a lattice where each patch feels only its four nearest neighbours. Warming speed barely mattered, and there were very few early-warning signals before the whole reef collapsed. I'd like to look at that further once the model is tuned to real reef data.",
                  "The next step was real data: how much heat can Scott Reef's corals take? The model now runs on NOAA's degree heating weeks (DHW), a measure of heat built up over weeks, and each colony gets its own heat tolerance, similar between neighbours (a random-field Potts model). It is fitted by simulation-based inference to 65 bleaching surveys of Scott Reef in April 2016 by AIMS, the Australian Institute of Marine Science. What agrees with the data: once colonies differ in tolerance, the model reproduces the April surveys. What the data can't settle: two very different reefs reproduce them equally well, a sensitive one that bleaches from about 4 DHW (NOAA's alert level) and a tolerant one that holds out to about 13 DHW. A single survey from February or March would tell them apart, and none exists. What points one way: AIMS reported widespread coral death at Scott Reef in early April, which only the sensitive reef predicts. The next phase of this project is better data: earlier and denser surveys of the reef."],
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
    dict(num="004", key="016", tag="earth", tag_label="Earth systems", status="in progress",
         folder="016-sahel-desertification", title="Sahel desertification as a lattice model",
         summary=["This continues the theme of earth systems as lattices, and their links back to physics. Earth-observation data comes as rasters, plants interact with their neighbours, and soil health and soil moisture behave like underlying fields, so the parallels with lattice models in physics are worth exploring. Desertification is a pressing climate problem I have always been interested in, and Kéfi et al.'s 2007 Nature paper on vegetation patterns and imminent desertification inspired me to look at it this way. The model is their probabilistic cellular automaton: each cell is vegetated, empty but fertile, or degraded, and bare soil recovers faster next to vegetation (facilitation), the same neighbour coupling as the coral reef's Potts model. With strong facilitation the system shows hysteresis: recovering from desert takes much more rainfall than the collapse did. The mean-field theory, which ignores space, overstates how stuck it gets.",
                  "The patch structure gives a much clearer early warning than total cover. As rainfall falls, the largest patch drops from 90% of all vegetation to 6% while cover is still near a half, well before the collapse, so tracking patch sizes in satellite imagery would warn of decline where average greenness would not. I drove the lattice with real rainfall at two Sahel sites: Gourma in Mali, which re-greened after the droughts, and Fakara in Niger, which did not. The rainfall data was a problem. Sahel rain falls in short, local storms, and averaging it over large grid boxes damps the signal: ERA5 came out about 35% too dry and agreed poorly with IMERG, so the runs use CHIRPS, which blends satellite estimates with rain gauges. As a stress test, the 1980s drought takes the lattice just below its tipping point, but too briefly to collapse it. Rainfall also predicted re-greening and decline less well than I expected: at Fakara greenness hardly follows the rain, and land use matters more.",
                  "Played year by year as a strip of landscape beside each site's satellite record, the lattice loses about a quarter of its cover through the 1980s at both sites; MODIS greenness follows it loosely at Gourma and not at all at Fakara. Work in progress: testing how well the model tracks long-term desertification, not only tipping points, and the covariates behind land being lost and coming back, such as grazing, cropping and soil."],
         stack="Python · Numba cellular automaton · pair approximation · percolation · Sentinel-2 · MODIS",
         hero=("figures/fig1_hysteresis.png", "Vegetation cover as rainfall falls and rises again, for three strengths of facilitation"),
         steps=[("Facilitation on a lattice", "A three-state lattice; facilitation f couples each cell to its neighbours.", "figures/fig1_hysteresis.png"),
                ("Theory against simulation", "Mean field and pair approximation beside the lattice.", "figures/fig2_theory.png"),
                ("Patch sizes as a warning", "The largest patch's share collapses before cover does; large patches vanish first.", "figures/fig3_early_warning.png"),
                ("Satellite patterns", "Sentinel-2 NDVI at Gourma and Fakara beside the model lattice.", "figures/fig4_patterns.png"),
                ("Compare rainfall products", "ERA5, CHIRPS and IMERG over each site: ERA5 is too dry and follows the satellites poorly.", "figures/fig6_rain_sources.png"),
                ("Play it beside the satellites", "Each site as a strip of lattice, year by year, beside its Sentinel-2 pattern and MODIS greenness.", "figures/fig7_sites_animation.gif"),
                ("Drive with real rain", "The lattice driven by CHIRPS rainfall, 1950-2025, against MODIS greenness from 2000.", "figures/fig5_sites.png")],
         results=[("figures/fig1_hysteresis.png", "Hysteresis"), ("figures/fig2_theory.png", "Theory against simulation"),
                  ("figures/fig3_early_warning.png", "Early warning"), ("figures/fig5_sites.png", "Two sites"),
                  ("figures/fig6_rain_sources.png", "Three rainfall products")]),
    dict(num="005", key="003", tag="earth", tag_label="Earth systems", status="real data",
         folder="003-po-valley-downscaling", title="Po Valley mesoclimate, physics-informed machine learning",
         summary=["In my work in quantitative climate risk at Wieldmore I became interested in regional climate models: smaller, region-specific models of a mesoclimate, especially for Europe's industrial belts. A region like the Po Valley is small enough to put a PDE mesh and machine learning on directly, and it sits between two rich sources: ERA5 and Copernicus gridded data, and a dense network of weather stations. The interesting question is what you give up when you leave a physically continuous system like ERA5. Once you cut out a region and enforce boundaries, you are at the mercy of the boundary conditions. The aim was a calibrated model of daily maximum temperature for the Po Valley that matches every station reading exactly.",
                  "Three approaches were compared against ERA5-Land and the standard statistical method, regression with kriged residuals. First, physics: a simplified heat-budget equation solved on a 1 km grid, with ERA5-Land on the boundary and satellite surface temperature heating the air from below, then adjusted so the surface passes exactly through every station reading. XGBoost is used to bridge the physical equation and the anchored station points. Second, a U-Net, the standard image-to-image network in downscaling, trained to reproduce the physics surface from coarse maps alone. Third, a physics-informed U-Net trained on the stations themselves, whose loss adds the error in the heat-budget equation at every grid cell to the error at the stations, so the physics fills the gaps between thermometers.",
                  "Built and checked first on simulated fields with a known truth, it has now run on the real data: ERA5-Land, MODIS, Earth Engine terrain and 38 stations, scored at stations held out in 50 km blocks in 2023. Every regional model beats ERA5-Land by about 0.3 K (1.89 K down to about 1.60 K), and the best ones, kriging, the physics and the physics-informed network, are level with each other. The physics earns its place in the network: the heat budget in the loss takes it from 1.71 K to 1.60 K, and anchored to the stations it is the best model on the hottest days. Next are the denser ARPA station networks, to separate the best models, and better benchmarking against ERA5 alone."],
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
    dict(num="006", key="008", tag="markets", tag_label="Markets", status="in progress",
         folder="008-spanish-solar-portfolio", title="Correlated risk structures in a Spanish solar portfolio",
         summary=["A fleet of solar plants carries correlated risk. If each site's P95, its output in a bad year, is worked out on its own, the fleet's bad year is underpriced, because the same clouds cover many sites at once. This project builds the framework for measuring that shared risk, the step that has to come before simulated weather or stochastic event sets can price it. Generation is proxied by ERA5 surface solar radiation for 25 Spanish solar regions in 2023, expressed as the clear-sky index: the share of the possible sunlight that gets through the cloud. The correlation between two sites falls with distance, and how far the clouds reach sets the scale: it drops to 1/e over about 350 km in winter, 440 km in spring and summer, and 670 km in autumn. In risk terms the portfolio of 25 sites behaves like only 3-4 independent ones.",
                  "ECMWF runs two forecast models side by side: IFS, its physics model, and AIFS, an AI model trained on ERA5. Their daily solar forecasts for the sites, 1 to 7 days ahead, were scored against ERA5. For risk, the useful finding is that forecast errors are far more local than the weather itself: they decorrelate over about 170-230 km, against about 500 km for the weather. Next is to use both models to build a stochastic event set of correlated low-solar periods, add more widely spread sites in different weather systems, bring in power prices, and move to CERRA at 5.5 km, since ERA5's 31 km grid smooths out small clouds."],
         stack="Python · ERA5 · clear-sky index · spatial correlation · effective number of sites · AIFS · IFS · corrlib",
         hero=("figures/cover.png", "Correlation with Seville by season, and against distance for every site pair"),
         steps=[("Build the dataset", "ERA5 solar radiation and cloud over Iberia for 2023, in Anemoi format, the layout ECMWF's AI forecast models read.", "figures/fig1_two_weeks.png"),
                ("Measure the reach", "Correlation of clear-sky index against distance, by season.", "figures/fig2_correlation_vs_distance.png"),
                ("Remove the sun", "A daily shape every site shares, left by the clear-sky model, is subtracted before correlating.", "figures/fig0_daily_shape.png"),
                ("Month by month", "The same fit for each month of 2023.", "figures/fig3_monthly_reach.png"),
                ("Count independent sites", "Effective number of sites, raw and cleaned, by season.", "figures/fig4_effective_sites.png"),
                ("Two forecast models", "AIFS and IFS daily solar forecasts, 1-7 days ahead, scored against ERA5 for each site and for the fleet.", "figures/fig5_forecast_skill.png"),
                ("Shared forecast errors", "Forecast errors against distance, beside the weather's own reach.", "figures/fig6_error_reach.png")],
         results=[("figures/hero.png", "The reach of the weather"), ("figures/fig2_correlation_vs_distance.png", "Correlation against distance"),
                  ("figures/fig4_effective_sites.png", "Effective sites by season"), ("figures/fig5_forecast_skill.png", "Forecast skill, IFS and AIFS"),
                  ("figures/fig6_error_reach.png", "How far forecast errors reach"), ("figures/fig7_cloudy_week.png", "The worst miss")]),
    dict(num="007", key="013", tag="markets", tag_label="Markets", status="in progress",
         folder="013-coffee-forward-curves", title="Weather and coffee price correlation",
         summary=["There is a large literature on weather and coffee prices, and this project tests how much weather moves both beans, arabica from Brazil and robusta from Vietnam, from an importer's point of view. Monthly World Bank prices for 2004-2026 are taken first with the standard driver stripped out, the Brazilian real, as gas was for Italian power. The weather comes from ERA5 for each origin: frost and three-month dryness in Brazil's arabica belt, heat and dryness in Vietnam's Central Highlands, and El Niño. Weather moves both beans in both regions: Vietnam heat has a partial correlation of about 0.17 with each bean, and of the hottest tenth of months in Vietnam, 32% were also top-10% price rises against 10% by chance. A Gumbel copula, which captures extremes arriving together, puts that tail dependence at about 0.15, while a Gaussian copula would say zero.",
                  "The risk also compounds across origins. In the 16 months when both Brazil and Vietnam were hit at once, both beans rose about 3.5% a month, against roughly 1% when one origin was hit. The two beans spike together half the time (a Gumbel tail coefficient of 0.46, rising from about 0.31 in 2013 to 0.55 now), so buying from the other origin hedges an importer less and less when it matters, and a global hedge has to reflect joint weather risk. A Kalman filter on the arabica futures curve shows the market pricing Vietnam's 2024 heat into the convenience yield (a significant weather term, p = 0.004). Finally, does ECMWF's seasonal forecast help with the price? It beats climatology on Vietnam's weather (a skill score of 0.41 for heat), and fed through the weather-price relationship it lifts the importer's correct buy-or-wait calls from about 40% to 50% and does about 0.6-0.7 percentage points of the purchase price better per quarter than assuming a normal season. Its real value is in the tail: in the months when the forecast flagged Vietnam as unusually hot or dry, arabica rose 7.0% and robusta 5.7% over the next three months, against 1.4% and 0.9% on average, a result that holds outside the 2023-25 rally. For an importer, that is a signal worth hedging on."],
         stack="Python · ERA5 · ECMWF SEAS5 · partial correlation · tail dependence · Gumbel copula · DCC-GARCH · Kalman filter · corrlib",
         hero=("figures/fig8_stacked.png", "Arabica and robusta with the real, Brazil's dryness, Vietnam's heat and dryness and El Niño, the 2014 drought, 2021 frost and 2024 heat shaded"),
         steps=[("Strip out the real", "Each bean's monthly return regressed on the change in reais per dollar; the residual is the move the currency leaves.", "figures/fig8_stacked.png"),
                ("Correlate weather with price", "Gaussian-rank correlation of each hazard with each bean at lags of 0-6 months, with the 95% band.", "figures/fig10_lags.png"),
                ("Look at the tails", "Tail dependence and a Gumbel copula for extreme weather against extreme price moves; DCC-GARCH for the link between the beans through time.", "figures/fig11_dependence.png"),
                ("The two beans together", "The Gumbel copula of arabica against robusta, as density rings, with the joint spikes marked.", "figures/fig13_copula.png"),
                ("Compound events", "Months when both origins are hit at once, and what each bean did.", "figures/fig14_compound.png"),
                ("A weather-informed forward curve", "A Kalman filter on the arabica curve with Vietnam heat pushing the convenience yield.", "figures/fig15_kalman.png"),
                ("Test the seasonal forecast", "ECMWF SEAS5 fed through the relationship each quarter, 2008-2025: buy forward or wait, against a normal-season benchmark.", "figures/fig16_seasonal.png"),
                ("Hedge on the tail", "Buy forward only when the forecast flags an extreme season: after a hot or dry Vietnam forecast both beans rose 6-7% in three months.", "figures/fig17_tail_rule.png")],
         results=[("figures/fig17_tail_rule.png", "Price change after an extreme-season forecast"), ("figures/fig13_copula.png", "Gumbel and Gaussian copulas, arabica vs robusta"), ("figures/fig14_compound.png", "Compound weather events"),
                  ("figures/fig12_bean_tail.png", "Arabica-robusta tail dependence"), ("figures/fig9_scatter.png", "Monthly moves against weather"),
                  ("figures/fig15_kalman.png", "Convenience yield and Vietnam heat")],
         maps=[("maps/013-coffee-belt.html", "Interactive: the eight regions of the frost index on the worst frost nights since 1990.")]),
    dict(num="008", key="014", tag="markets", tag_label="Markets", status="complete",
         folder="014-copper-satellite-signals", title="EO proxies for copper production intensity: an alternative data method",
         summary=["The devastating storms in Chile got me interested in how Earth observation can both help anticipate events like these and show their impact on industrial zones. Heavy industry is a good subject because it can be measured in so many ways: a large plant footprint, shipping data, and heat from energy-intensive furnaces. Each gives a way to estimate production, and so a downstream view of where prices are likely to go, or why they went the way they did. Copper suits this well, because its supply chain is short and concentrated: concentrate leaves a handful of Chilean and Peruvian ports, and it is smelted in a few dozen plants. Using Sentinel-2's shortwave infrared bands I detect the thermal signatures of smelter furnaces, and ship traffic at the copper ports comes from IMF PortWatch, built from the AIS position beacons that large ships carry. Ports that ship forestry, salmon and fishmeal serve as placebos.",
                  "The project was fairly successful at measuring supply. Dry-bulk exports from Peru's copper ports track Peru's official copper exports (correlation 0.67, against 0.27 for the placebo ports), and exports from the port serving Grasberg fell 89% after the September 2025 mudslide. Smelter heat, from 9,900 Sentinel-2 passes over 24 sites since 2019, is detectable at 24 of 30 smelters. But neither ships nor heat predict the copper price a month ahead out of sample: in steady conditions this supply is already priced in. So the interesting cases are disruptions. In the central Chile storm of 15-21 July 2026, exports from the central ports fell to zero on the first day and recovered by 26 July while the northern ports kept shipping, and copper rose about 3% within the week: detection and price were days apart. The satellites went blind: the Caletones smelter had no clear Sentinel-2 pass for 39 days, and afterwards ran at about 57% of its June heat. Kazakhstan's 2012 cold snap, read from Landsat 7, tells the same story: snow hid the Balkhash smelter from December to March, and it came back cooler, though within a year-on-year decline. Optical satellites go blind in exactly the weather that causes disruptions, so radar and night-time thermal imagery are next, with heat intensity and duration against exports and prices."],
         stack="Python · IMF PortWatch (AIS) · Sentinel-2 · Earth Engine · rasterio · out-of-sample testing",
         hero=("figures/fig3_smelters.png", "Four copper smelters in Sentinel-2 shortwave infrared, hot pixels outlined"),
         steps=[("Watch the ports", "Daily dry-bulk exports at 11 copper ports, Grasberg's port and 7 placebos.", "figures/fig1_validation.png"),
                ("Check against truth", "Peru's central bank publishes monthly copper export volumes; the copper ports follow them, the placebos do not.", "figures/fig1_validation.png"),
                ("A real shock", "Amamapare before and after the Grasberg mudslide.", "figures/fig2_grasberg.png"),
                ("Find the furnaces", "A shortwave-infrared hot-spot test locates 24 of 30 smelters; a closed plant kept as a check shows its limits.", "figures/fig3_smelters.png"),
                ("Watch them run", "Hot pixels by month at each smelter, 2019-2026, compared year on year.", "figures/fig4_smelter_heat.png"),
                ("A disruption up close", "The July 2026 central Chile storm: port exports, smelter heat and the copper price, central against north.", "figures/fig5_chile_2026.png"),
                ("A second one, in the snow", "Balkhash through Kazakhstan's 2012 cold snap, from Landsat 7: snow hid it for three months.", "figures/fig6_kazakhstan_2012.png")],
         results=[("figures/fig5_chile_2026.png", "Central Chile storm, July 2026"), ("figures/fig1_validation.png", "Ships against official exports"), ("figures/fig2_grasberg.png", "Grasberg, September 2025"),
                  ("figures/fig3_smelters.png", "Smelters in shortwave infrared"), ("figures/fig4_smelter_heat.png", "Smelter heat over time")]),
    dict(num="009", key="007", tag="markets", tag_label="Markets", status="complete",
         folder="007-italian-power-volatility", title="Weather and the Italian power price",
         summary=["This project measures how much the weather moves the Italian power price once gas is taken out. Gas plants set the Italian price in most hours, so the price mostly follows TTF gas. The project strips that out first, modelling power relative to gas, so that what is left can be tied to the weather. It runs on real data for 2018-2026: Italy North day-ahead prices, Italian load, wind and solar, ERA5 temperature for eight cities, and TTF gas. XGBoost, a gradient-boosted tree model, fits the price relative to gas, because the weather's effect is not a straight line. SHAP, which splits each prediction into how much each input contributed, shows its shape: power is dearer relative to gas in cold weather and above about 27 °C, and cheapest around 18-25 °C. GARCH-MIDAS then links the price's volatility to the monthly count of extreme-weather days. Before the real run, that estimator was tested on simulated data to confirm it recovers a weather effect of known size.",
                  "Day by day, heat lifts power above gas: through summer 2026 the daily correlation with temperature was 0.41, and power ran about 11% higher relative to gas on days above 28 °C. Over the whole period, the weather matters for volatility in the opposite direction to a 2026 study that found extreme weather the main driver of Italian price volatility. Months with more extreme days have calmer prices relative to gas, because in a heatwave gas plants set the price every hour and power simply tracks gas. Mild, sunny months, when Italy's growing solar fleet sets the price for part of the day, are when it swings most. Even perfect knowledge of each month's extremes lowers the volatility forecast loss by only 0.7%, the ceiling on what a seasonal forecast could be worth. The next step is real forecasts: ECMWF's seasonal forecasts, tested on held-out years to see whether they help predict the price and its volatility."],
         stack="Python · XGBoost · SHAP · GARCH-MIDAS · QLIKE · Diebold-Mariano · Energy-Charts · ERA5",
         hero=("figures/fig10_daily_2026.png", "Summer 2026 day by day: power, gas, power relative to gas and temperature, days above 28 °C shaded"),
         steps=[("Day by day", "Through summer 2026 each hot spell lifted power above gas: a daily correlation of 0.41 with temperature, and about 11% higher relative to gas on days above 28 °C (0.52 and 19% in 2022).", "figures/fig10_daily_2026.png"),
                ("Take gas out first", "Weekly power tracked gas almost one for one in the 2022 crisis and hardly at all in the 2026 heatwave; the weather link rises in heatwave summers.", "figures/fig9_rolling.png"),
                ("Weather to price", "Price relative to gas; XGBoost beats a straight line on unseen years and SHAP finds a U-shape in temperature.", "figures/fig6_real_shap.png"),
                ("Weather to volatility", "GARCH-MIDAS: the extreme-day count is significant, with a negative sign.", "figures/fig7_real_volatility.png"),
                ("Method check", "On simulated data the estimator recovers the planted weather effect on average.", "figures/fig3_midas_recovery.png")],
         results=[("figures/fig10_daily_2026.png", "Summer 2026, day by day"), ("figures/fig10_daily_2022.png", "Summer 2022, day by day"), ("figures/fig8_stacked.png", "Power, gas and the weather, 2018-2026"), ("figures/fig9_rolling.png", "The gas link and the weather link through time"), ("figures/fig6_real_shap.png", "What drives the price"),
                  ("figures/fig7_real_volatility.png", "Volatility components"), ("figures/fig3_midas_recovery.png", "Estimator check (simulated)")]),
    dict(num="010", key="012", tag="markets", tag_label="Markets", status="maths note",
         folder="012-percolation-tranche-loss", title="Supply chain risk as network percolation",
         summary=["Inspired by Ecology for Bankers, in which Robert May, Simon Levin and George Sugihara asked what bankers could learn from ecologists (Nature, February 2008, seven months before Lehman Brothers collapsed). The main piece is a 16-page LaTeX note deriving the tools they used. May's stability bound says a large web of interacting parts, species or firms, stays stable only while the strength and density of its links stay below a limit, σ√(NC) < 1. It comes from the circular law: the eigenvalues of a large random matrix fill a disc, and once that disc crosses zero the system tips. Percolation thresholds are the network version: if a failure passes along each link with some probability, there is a sharp point above which it spreads to a large share of the network instead of dying out. The wiring matters as well as the number of links. In disassortative networks, where hubs connect mostly to small nodes, as in payment systems and pollination webs, the threshold doubles for the same number of links per node, so weak shocks die out. Pushed past it, they fail more completely than a randomly wired network, so a network that looks robust in normal times can hide a worse collapse.",
                  "The case study is supply chain risk when the Rhine runs low, as in 2018 and again in July 2026, when the Kaub gauge matched the 25 cm record. A network of 4,000 firms at Rhine-basin commercial hubs is calibrated so that a low-water month costs about 1% of German industrial output. That 1% does not pin the network down: economies anywhere from 6% to 89% of the way to their percolation threshold reproduce it, so the same observed loss fits a network that is safe and one close to tipping. What decides it is whether road and rail can take over from the barges; if they can't, the same low water costs about a third of output. The same low water is then modelled three ways, each firm simply disrupted or not, with identical failure chances: independently, with a standard one-factor correlation model, and through the network. In the worst 1% of months independent failures lose 1.8% of output, the network 2.3% and the correlation model 7.4%: one common shock makes the whole economy fail at once, while supply-chain dependence is local. Past the network's threshold the average loss itself jumps to 38%, which neither simpler model would predict from an ordinary year. Over a four-month episode, with firms staying down while they rebuild stocks, every model loses about 6% of one month's output, and the worst 1% runs from 8% (independent) through 10% (network) to 26% (correlated). The note also applies the same tools to structured credit."],
         stack="Python · random matrices · percolation · generating functions · directed networks · folium · LaTeX",
         hero=("figures/fig4_rhine_map.png", "The Rhine at its 25 cm record: the network as calibrated to 2018, and with road and rail strained past the threshold"),
         steps=[("May's bound", "Community-matrix eigenvalues fill a disc of radius σ√(NC); stability is lost sharply at 1.", "figures/fig1_may_stability.png"),
                ("Percolation", "The giant failure cluster appears at T = <k>/(<k²> - <k>).", "figures/fig2_percolation_surface.png"),
                ("Disassortative wiring", "Same degrees, rewired: the threshold doubles, then the order reverses.", "figures/fig3_disassortativity.png"),
                ("The Rhine runs dry", "One aggregate number fixes a line of possible economies, not a point.", "figures/fig5_rhine_futures.png"),
                ("Three ways to model it", "Independent, correlated and network failures with the same chances: the tails differ, and past the threshold the average moves.", "figures/fig8_three_models.png"),
                ("Structured credit", "At equal mean loss, risk moves up the capital structure.", "figures/fig7_equal_mean.png")],
         results=[("figures/fig8_three_models.png", "Independent, correlated and network models"), ("figures/fig5_rhine_futures.png", "Three economies that all match 2018"), ("figures/fig7_equal_mean.png", "Equal mean, different tails"),
                  ("figures/fig3_disassortativity.png", "Same degrees, different wiring"), ("figures/fig6_tranche_switch.png", "The senior tranche switches on")],
         maps=[("maps/012-rhine-cascade.html", "Interactive: disruption probability for every firm at Kaub 25 cm, as calibrated and with substitution strained.")]),
    dict(num="011", key="005", tag="signals", tag_label="Signals", status="complete",
         folder="005-seismic-denoiser", title="Seismic denoiser",
         summary=["Seismology is built on signal processing, which ties it to my other projects, and earth systems are where my passion in applied mathematics lies. Small earthquakes under Los Angeles are often buried in traffic and other noise. I took 3,000 of the noisiest recordings (the bottom fifth by signal-to-noise) of small, local earthquakes from the Southern California Seismic Network, from a dataset where analysts have marked each P-wave arrival and its first motion. The P wave is the first wave to arrive from an earthquake. The time it lands at each station is used to locate the quake, and whether the ground first moves up or down at each station (the first motion) shows how the fault slipped. Earthquake catalogues and later reanalysis are built on these two numbers, so they are what any denoising has to preserve. With so many denoising methods available, the question was whether any of them can make these noisy recordings usable.",
                  "I picked arrivals with an STA/LTA trigger, the standard picker in seismology, and calibrated it and a first-motion estimator on quiet recordings, where they agree with the analysts 99% and 97% of the time. On the noisy set I compared a bandpass filter, wavelet thresholding, a random-matrix-theory denoiser, and wavelets followed by random matrix theory. Random matrix theory looked best, picking 98% of arrivals, but only because every recording had its arrival at the same point in the window. With the arrivals moved at random it fell to 60%, against 56% with no denoising at all. Wavelets raised the signal-to-noise ratio by about 3 dB but flipped the first motion on about one trace in fourteen. A plain bandpass filter was the only method that helped (from 55% to 63% of arrivals picked) without changing any first motions.",
                  "The dataset holds single-station recordings, so to test combining sensors I built a synthetic array: 16 sensors, one wave crossing them, and noise from a road shared between neighbouring sensors. Minimum-variance (Capon) beamforming, which weights each sensor using the noise covariance, beats a simple average because it learns the shared road noise and cancels it. It only does so once the covariance is cleaned with shrinkage: raw weights need about 0.8 s of noise to estimate, cleaned ones work from 0.2 s."],
         stack="Python · STA/LTA · bandpass · wavelets · random matrix theory · minimum-variance beamforming · corrlib",
         hero=("figures/cover.png", "A buried wave, before and after: one sensor, the average, the optimal stack"),
         steps=[("Calibrate on quiet traces", "Picker and first-motion estimator agree with analysts on 99% and 97% of clean recordings.", "figures/fig1_one_trace.png"),
                ("Score on noisy ones", "Five methods, with and without a random shift of the arrival.", "figures/fig2_scoreboard.png"),
                ("Stack an array", "Sensors near a road share noise; the covariance finds and cancels it.", "figures/fig3_array.png"),
                ("How much data?", "Raw optimal weights need ~0.8 s of noise to beat averaging; cleaned weights win from 0.2 s.", "figures/fig4_crossover.png")],
         results=[("figures/fig2_scoreboard.png", "Scoreboard"), ("figures/fig1_one_trace.png", "One noisy trace"),
                  ("figures/fig4_crossover.png", "The crossover"), ("figures/hero.png", "Gain against array size")]),
    dict(num="012", key="004", tag="signals", tag_label="Signals", status="complete",
         folder="004-corrlib-correlation-toolbox", title="corrlib, a correlation library",
         summary=["A small Python library I built to support these projects, since most of them involve some kind of correlation, signal processing, filtering or data assimilation. I wanted one set of tools I knew worked, so that when I code with AI agents, the tools they call are always consistent and correct. Building it also made me learn the exact mathematics behind each method. It covers correlation measures (Pearson, rank, Gaussian-rank, partial, distance, tail dependence and lead-lag); estimators for messy data, such as prices recorded at irregular, unmatched times (Hayashi-Yoshida) and samples that are not independent (effective sample size, block bootstrap); factor removal; random-matrix cleaning (clipping, Ledoit-Wolf and nonlinear shrinkage); and array stacking.",
                  "It is tested against established libraries: its rank correlations match SciPy's spearmanr and kendalltau, and its Ledoit-Wolf shrinkage matches scikit-learn's (59 tests in all). The Spanish solar project (006) compares sites with Correlator(measure='gaussian_rank', clean='nonlinear_shrinkage', effective_n='bartlett') and correlation_measures.gaussian_rank. The seismic denoiser (011) weights its sensors with random_matrix_cleaning.clean and array_stacking."],
         stack="Python · random matrix theory · Ledoit-Wolf · pytest",
         hero=("figures/cover.png", "Forty stocks, market removed and cleaned: the sectors appear"),
         steps=[("Measure", "Pearson, rank, Gaussian-rank, partial, distance and tail-dependence measures, all one contract.", "figures/fig1_same_number_different_reality.png"),
                ("Remove", "Regress out a known factor or strip the top modes, with the noise band corrected for what was removed.", "figures/fig5_correlator_summary.png"),
                ("Clean", "Clipping, Ledoit-Wolf and nonlinear shrinkage, tested against matrices with a known truth.", "figures/fig4_noise_band.png"),
                ("Stack", "Minimum-variance weights are the Capon beamformer: one formula for portfolios and sensor arrays.", "figures/fig6_stacking.png")],
         results=[("figures/hero.png", "Sectors appear once the market is out"), ("figures/fig2_tail_dependence.png", "Crashing together"),
                  ("figures/fig3_epps_effect.png", "The Epps effect"), ("figures/fig4_noise_band.png", "Signal outside the noise band")]),
    dict(num="013", key="015", tag="markets", tag_label="Markets", status="complete",
         folder="015-commodity-option-hedging", title="Hedging Italian wheat through Russia's 2010 export ban: producer and miller",
         summary=["In commodities the hedger who matters most is often the producer: a farm that knows roughly how much it will harvest but not what it will be paid. This project tests the standard producer hedges against one real shock. Russia had its worst heatwave on record through July 2010 and banned grain exports on 5 August, and European wheat, competing with Black Sea grain for the same buyers, rose 39%, from 136 euros a tonne on 3 May to 189 on 31 August. An Italian soft-wheat producer hedges on 3 May the crop it sells on 31 August, choosing between eight standard hedges: no hedge, selling all or half forward with futures, buying a put, a zero-cost collar (a put paid for by selling a call), a put spread, a three-way fence, and layering futures sales month by month. The options are priced by Black (1976), the same model used in the Asian option pricer (014). Euronext milling wheat isn't freely available for 2010, so CBOT wheat converted to euros stands in for it.",
                  "In hindsight the producer did best unhedged, since a price spike is good news for a seller, and of the hedges the put and the put spread kept most of the rally while futures gave all of it up and the collar was capped at 145 euros. Judged on 3 May, before the event, the ranking reverses: by the average of the worst 5% of outcomes, short futures and the collar protected best and no hedge was the most dangerous. The right hedge depends on what the producer can't afford: a farm that must cover its costs should lock in a price, one that can stand a bad year but not a missed rally should buy puts. The other side of the market tells the opposite story. An Italian miller buying wheat saved €53 a tonne by buying futures, and €43-46 with a call or a zero-cost collar, while the cheaper call spread and three-way, capped at +15%, saved only €14 in a 39% rise. The same weather shock in another country was a windfall for one side and a loss for the other. Adding yield risk changes the producer's answer: when the harvest falls with the price rise, the best hedge drops from 100% of the expected crop to about half, and a drought-hit producer fully hedged in 2010 ended with €74 per tonne against €127 unhedged. Next are Euronext prices in place of CBOT."],
         stack="Python · Black-76 · futures and option hedges · Monte Carlo · wheat in euros",
         hero=("figures/fig5_wheat_2010.png", "Wheat in euros per tonne through 2010: the hedge window, the heatwave, the export ban and every strike"),
         steps=[("Set the hedges", "On 3 May 2010: futures at 136 euros a tonne, an at-the-money put at 9.8, a collar call at 145 and a three-way call at 152, priced at the 60-day volatility.", "figures/fig7_wheat_payoffs.png"),
                ("Run the shock", "The heatwave and the export ban take wheat to 189 euros a tonne by the sale date.", "figures/fig5_wheat_2010.png"),
                ("Score in hindsight and in advance", "What each hedge paid in 2010, against the range a producer could have expected on 3 May.", "figures/fig6_wheat_revenue.png"),
                ("Add yield risk", "When the harvest falls as the price rises, the best hedge ratio drops from 100% to about half.", "figures/fig8_yield_risk.png"),
                ("The option seller's side", "The earlier version: options sold and delta-hedged on six commodities since 2002; in a shock the loss is set by the volatility sold.", "figures/fig3_variance_surprise.png")],
         results=[("figures/fig6_wheat_revenue.png", "Producer revenue and miller cost by hedge"), ("figures/fig7_wheat_payoffs.png", "Revenue and cost against the wheat price"),
                  ("figures/fig5_wheat_2010.png", "Wheat in euros per tonne, 2010"), ("figures/fig1_frontier.png", "Option seller: error against cost")]),
    dict(num="014", key="006", tag="markets", tag_label="Markets", status="complete",
         folder="006-option-pricer", title="Asian option pricer",
         summary=["A learning project. I learned option pricing from Mark Joshi's The Concepts and Practice of Mathematical Finance, before and during my time as a quantitative analyst at Wieldmore, where I found myself dealing with all kinds of options, not just European ones, Asian options among them. It tied in surprisingly well with the PDEs and numerical methods from my physics degree. My main interest is commodities, so this is the pricing groundwork for that: an Asian option pays on the average price over a period, which is how commodity buyers usually hedge.",
                  "Prices are built three independent ways and checked against each other: Monte Carlo, a finite-difference solver (tested first on European options), and Večeř's PDE, which turns an Asian option into a problem in one space variable however many fixings it has. To make the Monte Carlo practical, the exact price of the geometric-average Asian option is used as a control variate, which cuts the noise by 1,100 to 7,200 times. Run on coffee, cocoa and sugar with seasonal volatility, it reproduces the well-known results: an Asian option's delta fades as the average locks in, but most of its hedging risk sits just before averaging starts, and ignoring seasonal volatility changes the price but not how well the hedge works. The same pricing and delta hedging carry into my commodity option hedging project (013)."],
         stack="Python · Monte Carlo · control variates · Crank-Nicolson/SOR · Večeř PDE · delta hedging",
         hero=("figures/cover.png", "Monte Carlo: simulated coffee prices and the average an Asian option pays on"),
         steps=[("Check the solver", "Second-order convergence measured on European options.", "figures/fig2_pde_convergence.png"),
                ("Let volatility follow the calendar", "Volatility in coffee, cocoa and sugar changes through the year, so the pricer lets it change through time.", "figures/fig8_seasonal_vol.png"),
                ("Price an Asian", "The exact geometric-Asian price as a control variate cuts Monte Carlo noise 1,100-7,200x; Večeř's PDE agrees to within one standard error.", "figures/fig9_control_variate.png"),
                ("Hedge it", "A hedge simulator finds where the risk lives: just before the averaging starts.", "figures/fig10_hedging_risk_timing.png")],
         results=[("figures/fig9_control_variate.png", "The control variate"), ("figures/hero.png", "Delta through time"),
                  ("figures/fig8_seasonal_vol.png", "Seasonal volatility in softs"), ("figures/fig10_hedging_risk_timing.png", "Where hedging risk lives")]),
    dict(num="015", key="009", tag="physics", tag_label="Physics", status="undergrad",
         folder="earlier-work/pde-solvers-cpp", title="PDE systems by successive over-relaxation",
         summary=["Undergraduate numerical simulation work in C++. Laplace's equation is solved on the unit square, with fixed values on the boundary and fixed-potential objects inside the domain, first with Dirichlet and then with Neumann boundary conditions. Successive over-relaxation (SOR) is an iterative method: each grid point is repeatedly replaced by the average of its four neighbours, as in Gauss-Seidel, but each update is pushed beyond that average by a relaxation factor between 1 and 2, which cuts the number of sweeps needed to converge many times over.",
                  "I later ported the solver to Python with Numba to study the compute cost alongside the solution: how the number of sweeps depends on the relaxation factor and the grid size. The best factor climbs towards 2 as the grid refines, close to the theoretical 2 / (1 + sin(π/(N-1))); on a 253 x 253 grid the optimal factor converges in 760 sweeps against 4,047 at 1.8. The same SOR machinery was then applied to the Black-Scholes equation, where it matches the closed-form price to within 0.003. A companion lab solved the time-independent Schrödinger equation in one dimension with the Numerov method, for a finite well and a harmonic potential."],
         stack="C++ · Python · Numba · finite differences · SOR",
         hero=("figures/cover.png", "Laplace's equation solved by SOR: surface and contours"),
         steps=[("Solve Laplace's equation", "Over-relaxed Gauss-Seidel sweeps on a 253 x 253 grid: 760 sweeps at the optimal factor, against 4,047 at 1.8.", "figures/fig1_laplace_surface.png"),
                ("Map the cost", "Sweeps to converge across relaxation factor and grid size; the best factor climbs towards 2 as the grid refines.", "figures/fig2_sor_parameter_surface.png"),
                ("Solve Black-Scholes", "A standard call: the value over stock price and time to expiry, coloured by gamma, closing in on the payoff at expiry.", "figures/fig5_black_scholes_surface.png")],
         results=[("figures/fig5_black_scholes_surface.png", "Black-Scholes surface"), ("figures/fig2_sor_parameter_surface.png", "SOR cost surface"),
                  ("figures/fig1_laplace_surface.png", "Laplace surface"), ("figures/original_pde_surfaces.png", "The original C++ surfaces")]),
    dict(num="016", key="010", tag="physics", tag_label="Physics", status="undergrad",
         folder="earlier-work/potts-monte-carlo-cpp", title="The Potts model by Monte Carlo",
         summary=["Undergraduate Monte Carlo work in C++. The Potts model generalises the Ising model: each site on a two-dimensional lattice takes one of q states, and the energy counts the mismatched neighbour pairs. I sampled it with the Metropolis algorithm on a 24 x 24 lattice with periodic boundaries, 10,000 steps per temperature with the first 4,000 discarded for thermalisation, and measured the magnetisation and its variance as the inverse temperature β changes.",
                  "For q = 3 the transition is continuous, near β ≈ 1.06, close to the exact value ln(1 + √3) ≈ 1.005; for q = 5 it is first order and much sharper, near β ≈ 1.23, as theory expects for q above 4. The same model, scaled up and given biological rules, became the coral reef project (003)."],
         stack="C++ · Python · Numba · Metropolis Monte Carlo · statistical physics",
         hero=("figures/cover.png", "The lattice hot, at the critical point, and cold"),
         steps=[("Simulate the lattice", "Single-site Metropolis updates; snapshots from a 256 x 256 Numba port.", "figures/fig1_lattice.png"),
                ("Watch order appear", "Magnetisation jumps from about 0.1 to 0.9 over a narrow range of temperature.", "figures/fig2_magnetisation.png"),
                ("Find the transition", "Fluctuations peak at the critical point.", "figures/fig3_fluctuations.png")],
         results=[("figures/fig1_lattice.png", "Cooling through the transition"), ("figures/fig2_magnetisation.png", "Magnetisation"),
                  ("figures/fig3_fluctuations.png", "Fluctuations"), ("figures/original_potts_results.png", "The original C++ results")]),
    dict(num="017", key="011", tag="physics", tag_label="Physics", status="undergrad",
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
    '006': '<p class="credit"><sup>&dagger;</sup>Learned from Joshi, <em>The Concepts and Practice of Mathematical Finance</em>. Control variate from Kemna &amp; Vorst (1990); one-dimensional Asian PDE from Ve&ccaron;e&rcaron; (2001). Prices from Yahoo Finance via yfinance.</p>',
    '000': '<p class="credit"><sup>&dagger;</sup>Builds on the open-shell porphyrins of <a href="https://doi.org/10.1021/jacs.0c07781">Sun, Mateo, Robles et al. (2020)</a> and <a href="https://doi.org/10.1002/advs.202105906">Sun et al. (2022)</a>; compared with <a href="https://doi.org/10.1038/s42005-023-01231-y">Gao, Mench&oacute;n, Garcia-Lekue &amp; Brandbyge (2023)</a> and the chemical spin switch of W&auml;ckerlin et al. (2010). FHI-aims from Blum et al. (2009).</p>',
    '009': '',
    '010': '<p class="credit"><sup>&dagger;</sup>Exact critical point from Baxter (1973); Metropolis et al. (1953).</p>',
    '011': '',
    '012': '<p class="credit"><sup>&dagger;</sup>Builds on <a href="https://doi.org/10.1038/451893a">May, Levin &amp; Sugihara (2008)</a>, May (1972), Newman, Strogatz &amp; Watts (2001), Watts (2002), Gai &amp; Kapadia (2010) and Vasicek (2002). Low-water effect from <a href="https://doi.org/10.1515/ger-2022-0077">Ademmer, Jannsen &amp; Meuchelb&ouml;ck (2023)</a>. Basemap: Natural Earth.</p>',
    '013': '<p class="credit"><sup>&dagger;</sup>Kalman filter on Schwartz (1997) dynamics; DCC from Engle (2002); copulas after Joe (1997). Prices from the World Bank Pink Sheet; El Ni&ntilde;o from NOAA CPC; seasonal forecasts from ECMWF SEAS5 via Copernicus. Forecasts from ECMWF IFS and NOAA GFS via the Open-Meteo archive; ERA5 (<a href="https://doi.org/10.1002/qj.3803">Hersbach et al. 2020</a>). Prices and the Brazilian real from Yahoo Finance.</p>',
    '014': '<p class="credit"><sup>&dagger;</sup>Ship data from <a href="https://portwatch.imf.org">IMF PortWatch</a> (Arslanalp, Koepke &amp; Verschuur 2021); official exports from the Banco Central de Reserva del Per&uacute;. Hot-spot test after Murphy et al. (2016). Contains modified Copernicus Sentinel-2 data, via Microsoft Planetary Computer.</p>',
    '015': '<p class="credit"><sup>&dagger;</sup>Builds on Black (1976); the option seller&rsquo;s side on Leland (1985), Whalley &amp; Wilmott (1997) and Hull &amp; White (2017). CBOT wheat futures and EUR/USD via Yahoo Finance.</p>',
    '016': '<p class="credit"><sup>&dagger;</sup>Builds on K&eacute;fi et al. (2007), Rietkerk et al. (2004) and Scanlon et al. (2007). Sites after Dardel et al. (2014). Contains modified Copernicus Sentinel-2 data; MODIS NDVI via the ORNL DAAC; rainfall from CHIRPS (<a href="https://doi.org/10.1038/sdata.2015.66">Funk et al. 2015</a>) and IMERG V07 via Earth Engine, and ERA5 via Open-Meteo.</p>',
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
    "006": lambda: draw_pipeline(
        "006", "Asian option pricer: three methods that check each other",
        ["Data", "Volatility", "Methods", "Check", "Outputs"],
        [("px", "Coffee, cocoa, sugar", "futures history", 0, 0, "input"),
         ("sv", "Seasonal volatility", "by calendar month", 1, 0, "step"),
         ("mc", "Monte Carlo", "geometric control variate", 2, 0, "step"), ("fd", "Finite differences", "solver checks", 2, 1, "step"),
         ("vc", "Vecer PDE", "one space variable", 2, 2, "step"),
         ("cmp", "Agreement", "within one standard error", 3, 1, "step"),
         ("price", "Asian prices", "softs", 4, 0, "output"), ("hedge", "Delta hedge", "where the risk sits", 4, 1, "output")],
        [("px", "sv", True), ("sv", "mc", True), ("sv", "vc", True), ("fd", "cmp", False), ("mc", "cmp", True), ("vc", "cmp", True),
         ("cmp", "price", True), ("mc", "hedge", True)],
        "A learning project, from Joshi's The Concepts and Practice of Mathematical Finance.",
        [("Input", "Coffee, cocoa and sugar futures prices."),
         ("Volatility", "Volatility that follows the calendar, estimated by month."),
         ("Methods", "Monte Carlo with the exact geometric-Asian price as a control variate, a finite-difference solver, and Vecer's one-dimensional PDE."),
         ("Check", "The methods agree to within one Monte Carlo standard error."),
         ("Output", "Asian option prices on softs, and a hedge simulator that shows where the risk sits.")]),
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
        "013", "Weather and coffee prices: two origins, an importer's view",
        ["Data", "Strip", "Dependence", "Forecast", "Outputs"],
        [("px", "Arabica, robusta", "World Bank monthly", 0, 0, "input"), ("brl", "Brazilian real", "per dollar", 0, 1, "input"),
         ("wx", "ERA5 weather", "Brazil, Vietnam", 0, 2, "input"), ("seas", "ECMWF SEAS5", "seasonal forecasts", 0, 3, "input"),
         ("res", "Real removed", "residual returns", 1, 0, "step"),
         ("cop", "Copulas, tails", "partial, Gumbel", 2, 0, "step"), ("dcc", "DCC-GARCH", "beans together", 2, 1, "step"),
         ("cmp", "Compound events", "both origins hit", 2, 2, "step"), ("kal", "Kalman filter", "forward curve", 2, 3, "step"),
         ("bt", "Backtest", "buy forward or wait", 3, 3, "step"),
         ("risk", "Weather risk", "both regions, in the tail", 4, 0, "output"), ("hedge", "Origin hedge", "fails when it matters", 4, 1, "output"),
         ("curve", "Weather in the curve", "Vietnam heat", 4, 2, "output"), ("dec", "Forecast value", "vs climatology", 4, 3, "output")],
        [("px", "res", True), ("brl", "res", True), ("res", "cop", True), ("wx", "cop", True), ("res", "dcc", True),
         ("wx", "cmp", True), ("res", "cmp", True), ("wx", "kal", False), ("seas", "bt", True), ("res", "bt", False),
         ("cop", "risk", True), ("dcc", "hedge", True), ("cmp", "hedge", True), ("kal", "curve", True), ("bt", "dec", True)],
        "Every step runs on real data; the forward curve covers 2024-2026.",
        [("Input", "Monthly arabica and robusta prices, the Brazilian real, ERA5 weather for both origins, El Nino and ECMWF seasonal forecasts."),
         ("Strip", "Each bean's return with the real regressed out."),
         ("Dependence", "Lags, partial correlation, tail dependence, Gumbel copulas, DCC-GARCH and compound events."),
         ("Forecast", "SEAS5 fed through the weather-price relationship each quarter: buy forward or wait, against climatology."),
         ("Output", "How weather moves both beans, why the origin hedge fails in joint extremes, a weather-informed forward curve, and what the forecast is worth.")]),
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
        "015", "Hedging Italian wheat through Russia's 2010 export ban",
        ["Data", "Price", "Hedges", "Score", "Outputs"],
        [("w", "CBOT wheat", "in euros per tonne", 0, 0, "input"), ("fx", "EUR/USD", "daily", 0, 1, "input"),
         ("vol", "60-day volatility", "before 3 May", 1, 0, "step"), ("b76", "Black-76", "puts and calls", 1, 1, "step"),
         ("prod", "Producer hedges", "futures, puts, collars", 2, 0, "step"), ("mill", "Miller hedges", "futures, calls, collars", 2, 1, "step"),
         ("hind", "Hindsight", "what 2010 paid", 3, 0, "step"), ("mc", "Monte Carlo", "as seen on 3 May", 3, 1, "step"),
         ("p", "Producer", "regretted hedging", 4, 0, "output"), ("m", "Miller", "saved by hedging", 4, 1, "output")],
        [("w", "vol", True), ("fx", "w", False), ("vol", "b76", True), ("b76", "prod", True), ("b76", "mill", True),
         ("prod", "hind", True), ("prod", "mc", True), ("mill", "hind", True), ("mill", "mc", True),
         ("hind", "p", True), ("mc", "p", True), ("hind", "m", True), ("mc", "m", True)],
        "CBOT in euros stands in for Euronext milling wheat, whose 2010 daily history is not freely available.",
        [("Input", "CBOT wheat converted to euros per tonne at each day's EUR/USD rate, 2010."),
         ("Price", "Options priced by Black (1976) at the 60-day volatility before the hedge date."),
         ("Hedges", "Eight standard structures for a producer selling and a miller buying."),
         ("Score", "What each paid in 2010, against the range expected on 3 May."),
         ("Output", "The same weather shock abroad: a windfall for the producer, a loss avoided by the hedged miller.")]),
    "016": lambda: draw_pipeline(
        "016", "Sahel desertification as a lattice model",
        ["Theory", "Model", "Signals", "Real sites", "Outputs"],
        [("mf", "Mean field", "no space", 0, 0, "input"), ("pa", "Pair approximation", "neighbour pairs", 0, 1, "input"),
         ("ca", "Kefi lattice", "facilitation", 1, 1, "step"),
         ("hy", "Hysteresis", "drying and wetting", 2, 0, "step"), ("ps", "Patch sizes", "percolation", 2, 1, "step"),
         ("rain", "CHIRPS rainfall", "IMERG as a check", 3, 2, "input"), ("ndvi", "MODIS, Sentinel-2", "greenness, patches", 3, 3, "input"),
         ("trap", "Hysteresis", "theory overstates it", 4, 0, "output"), ("warn", "Early warning", "patches break first", 4, 1, "output"),
         ("land", "Two sites", "land use, not only rain", 4, 2, "output")],
        [("mf", "hy", False), ("pa", "ca", False), ("ca", "hy", True), ("ca", "ps", True), ("hy", "trap", True),
         ("ps", "warn", True), ("rain", "land", True), ("ndvi", "land", True)],
        "Work in progress: long-term tracking, covariates of loss and recovery, and a lattice animation beside satellite imagery.",
        [("Theory", "Mean-field and pair-approximation equations for the three-state model."),
         ("Model", "A Numba lattice of vegetated, empty and degraded cells, with facilitation f."),
         ("Signals", "Hysteresis loops, and patch sizes and spanning clusters as the landscape dries."),
         ("Real sites", "Gourma and Fakara: CHIRPS rain drives the lattice, MODIS and Sentinel-2 check it."),
         ("Output", "How far theory overstates the trap, an early warning visible from space, and why rain alone cannot explain which site re-greened.")]),
}


def fig(src, caption, base, folder, lazy=True):
    url = f"{base}{folder}/{src}"
    return (f'<figure><img src="{html.escape(url)}" alt="{html.escape(caption)}"'
            f'{" loading=\"lazy\"" if lazy else ""}><figcaption>{html.escape(caption)}</figcaption></figure>')


def project_html(p, base, credit, pipeline_panel, repo_link):
    n = p["key"]            # fixed id for this project; the number shown is p["num"]
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
        <span class="num">{p["num"]}</span><span class="title">{html.escape(p["title"])}</span>
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
        n = p["key"]
        #find this project's block in the previous page by its folder, which never changes
        at = old_list.find(f'{p["folder"]}/')
        block_start = -1 if at < 0 else old_list.rfind('<li class="project"', 0, at)
        next_item = old_list.find('<li class="project"', at + 1) if at >= 0 else -1
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
    new_page = new_page.replace("Most are variants of a\n    published model, changed in some way or applied to a particular case.",
                                "Most are variants of a\n    published model, changed in some way or applied to a particular case. All are side projects, built for fun.")
    out = os.path.join(HERE, "index.html" if publish else "index_preview.html")
    io.open(out, "w", encoding="utf8").write(new_page)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
