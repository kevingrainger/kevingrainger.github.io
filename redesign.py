"""Redesign of the project list (approved from mockup.html, 10 Nov 2026), applied by build_index.py:
click-to-expand rows with 96 x 60 thumbnails; an opened row shows a short summary that wraps
round a three-image gallery (sides alternate); the card's full text moves into "view more"."""
import os, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)  # the Portfolio folder that holds the project folders
THUMBS = os.path.join(HERE, "images", "thumbs")

# folder -> (thumbnail source, [large, small, small])
PICK = {
    "earlier-work/dft-porphyrin-networks": ("cover_znextra_homo.png", ["fig15_chain_orbitals.png", "fig14_orbital_atlas.png", "fig8_oxo_spin_by_element.png"]),
    "002-olive-grove-xylella": ("hero_no_control.png", ["fig0_animation.gif", "hero.png", "fig_real_grove.png"]),
    "001-coral-reef-tipping-points": ("cover.gif", ["cover.gif", "fig8_scott_reef_2016.png", "fig10_tipping_crw.png"]),
    "016-sahel-desertification": ("fig4_patterns.png", ["fig15_landsat_animation.gif", "fig1_hysteresis.png", "fig3_early_warning.png"]),
    "003-po-valley-downscaling": ("real/cover_real.png", ["real/cover_real.png", "real/fig8_physics_informed_real.png", "real/fig4_footprints_real.png"]),
    "008-spanish-solar-portfolio": ("cover.png", ["cover.png", "fig10_event_set.png", "fig6_error_reach.png"]),
    "013-coffee-forward-curves": ("fig13_copula.png", ["fig8_stacked.png", "fig13_copula.png", "fig17_tail_rule.png"]),
    "014-copper-satellite-signals": ("fig3_smelters.png", ["fig9_ships_radar.gif", "fig3_smelters.png", "fig5_chile_2026.png"]),
    "007-italian-power-volatility": ("cover.png", ["fig10_daily_2026.png", "fig6_real_shap.png", "fig12_daily_drivers.png"]),
    "012-percolation-tranche-loss": ("fig4_rhine_map.png", ["cover.gif", "fig4_rhine_map.png", "fig8_three_models.png"]),
    "005-seismic-denoiser": ("cover.png", ["cover.png", "fig2_scoreboard.png", "fig3_array.png"]),
    "004-corrlib-correlation-toolbox": ("cover.png", ["cover.png", "fig2_tail_dependence.png", "fig4_noise_band.png"]),
    "015-commodity-option-hedging": ("fig5_wheat_2010.png", ["fig5_wheat_2010.png", "fig6_wheat_revenue.png", "fig8_yield_risk.png"]),
    "006-option-pricer": ("cover.png", ["cover.png", "fig9_control_variate.png", "fig8_seasonal_vol.png"]),
    "earlier-work/pde-solvers-cpp": ("cover.png", ["cover.png", "fig2_sor_parameter_surface.png", "fig5_black_scholes_surface.png"]),
    "earlier-work/potts-monte-carlo-cpp": ("cover.png", ["fig1_lattice.png", "fig2_magnetisation.png", "fig3_fluctuations.png"]),
    "earlier-work/higher-order-odes-cpp": ("cover.png", ["fig4_shooting.png", "fig2_convergence.png", "fig1_rk4_vs_exact.png"]),
}

SUMMARY = {
"001": "My undergraduate capstone at Trinity College Dublin, in Prof. Cormac McGuinness's Surface, Interface Physics &amp; X-ray Spectroscopy Group. The aim was to find the band gap of metal-porphyrin chains and where their HOMO and LUMO states are located, using density functional theory in FHI-aims.</p><p>The project found that the carbon bridge between unit cells in the 1D chain can change the HOMO-LUMO gap, where the frontier states are located and whether the chain is magnetic. In zinc chains a fully fused bridge carries the HOMO along the whole chain, while a weak bridge leaves it on each unit. With iron and vanadium centres the metal's d orbitals move into the gap and shorten it, so the frontier states are on the metal. Weakly bonded chains carry unpaired electrons on their carbon backbone, while more strongly fused chains tend to pair them up. The simulations point to the weak bridge keeping each unit's orbitals separate, so each porphyrin keeps the unpaired electrons it has as a single molecule, while fusing joins them into bands along the chain.</p><p>Furthermore, it was found that an oxygen bound to the central metal can override the effect of the carbon bridge. The backbone spin disappears, leaving a single local spin on the metal-oxygen unit (S = 1 for iron, S = ½ for vanadium), and the HOMO-LUMO gap widens, from 0.34 to 0.64 eV in the fully fused iron chain.</p><p>This points towards potential for chemical sensors and molecular electronics, both of great interest with porphyrins (Paolesse et al., 2017), given the graphene-like conduction that fused porphyrin chains can display (Gao et al., 2023).",
"002": "<em>Xylella fastidiosa</em> is a bacterium that blocks a tree's water vessels. Since it was found near Gallipoli in 2013 it has killed millions of olive trees in southern Italy, and Schneider et al. (2020) estimate it could cost Italy €1.9 to 5.2 billion over 50 years if the dead groves are not replanted. This is what got me interested in modelling it. This project is a recreation of the agent-based model of <a href='https://doi.org/10.1038/s41598-019-44997-4'>Fierro, Liccardo &amp; Porcelli (2019)</a>, in which spittlebugs carry the bacterium from tree to tree, rebuilt light enough to be run and tuned many more times. The aim was to bring in percolation theory and look for planting spacings and felling patterns that break up the spread.</p><p>Via stochastic simulation, it was found that outbreaks are all or nothing. 39 of 40 simulated outbreaks infected the whole grove, and below roughly 16% chance of infection per spittlebug visit, outbreaks die out. With trees spaced 6 to 8 m apart, and spittlebug numbers per tree kept down by managing the ground cover, the infection no longer spreads through the whole grove. None of the felling patterns tried slowed the spread.",
"003": "Numerical simulation was one of my favourite modules at Trinity, and one of the models we built was the Potts model, a grid of cells each pulled towards the state of its neighbours. I have always been interested in how ecosystems collapse, and coral reefs are a clear case. In the global bleaching event of 2023-25, about 84% of the world's reef area had heat stress high enough to bleach coral (NOAA Coral Reef Watch, 2025). The best-known reef models, such as that of <a href='https://doi.org/10.1038/nature06252'>Mumby, Hastings &amp; Edwards (2007)</a>, are mean-field, where every patch of reef feels the average of the whole reef.</p><p>The aim was to rebuild my undergraduate Potts model of a reef, as a lattice of healthy coral, bleached coral, bare rock and seaweed, test how far the interactions between patches should reach, and fit it to a real bleaching event at Scott Reef in Western Australia in 2016.</p><p>Via stochastic simulation, it was found that the reef has hysteresis at every interaction range. Once heat kills enough coral, seaweed grows over it, and the coral only returns once the water is cooled well below where it was lost. The gap between warming and cooling is about 60% wider when every patch feels the whole reef than when it feels its four nearest neighbours.</p><p>Furthermore, it was found that two different reefs fit the 65 April 2016 surveys equally well, a sensitive one whose corals bleach from about 4.5 degree heating weeks and a tolerant one at about 12.7. Warmed slowly, the sensitive reef tips at +1.1 to 1.2 °C above the warmest-month mean and the tolerant one at +1.4 to 1.7 °C, and neither recovers on cooling. A single survey from February would tell the two apart, which points towards earlier and repeated reef surveys as the way to pin down how much heat a reef can take.",
"004": "The Sahel has been a fixation of mine since I first learned about it as a child, when I did a school science project on it with a chicken incubator and root fungi. In the droughts of the 1970s and 80s it lost much of its vegetation, and when the rain partly came back from the 1990s, so did the green, but not everywhere. This project is a recreation of the facilitation model of <a href='https://doi.org/10.1038/nature06111'>Kéfi et al. (2007)</a>, a spin-off of my coral reef lattice, in which bare soil recovers faster next to plants.</p><p>The aim was to find whether the lattice tips, and stays tipped, as rainfall falls and recovers, to compare it with theories that ignore space, and to drive it with real rain against satellite greenness at two Sahel sites and then 223 sites from Senegal to Chad.</p><p>Via stochastic simulation, it was found that with strong facilitation recovering from desert takes much more rain than the collapse did, and that the largest patch breaks up (90% of the vegetation to 6%) while the cover is still near a half, well before the collapse. Furthermore, it was found that rain alone does not explain the real sites. Gourma's greenness tracks its rain and Fakara's does not, and across the Sahel more used land greened less beyond its rain. With seed rain from outside the lattice, tested on 1982-2021 satellite records, the lattice matches rain and does slightly better year to year, but tipping cannot be told apart from rain in the data.</p><p>This points towards land use over time, rather than rain, as the missing driver, and towards testing prevention methods such as rotating grazing on simulated droughts.",
"005": "In my work in quantitative climate risk at Wieldmore I became interested in regional climate models, smaller region-specific models of a mesoclimate, especially for Europe's industrial belts. The Po Valley is one of them, and the Po basin produces about 40% of Italy's GDP. It is small enough to put a PDE mesh and machine learning on directly, and it has two rich sources of data, ERA5-Land, with boxes about 9 km across, and a network of weather stations.</p><p>The aim was a calibrated 1 km model of daily maximum temperature for the Po Valley that matches every station reading exactly. A heat-budget equation anchored to the stations was compared with a U-Net, a physics-informed U-Net, ERA5-Land and regression with kriged residuals, the standard statistical method. It was built and checked on simulated fields with a known truth, then run on real data from ERA5-Land, MODIS and 38 stations for the summers of 2021-2023.</p><p>On the real data, it was found that every regional model beats ERA5-Land by about 0.3 K at stations held out in 50 km blocks (1.89 K down to about 1.60 K). Kriging, the physics model and the physics-informed network are within 0.05 K of each other, and 38 stations cannot separate them. Furthermore, it was found that putting the heat budget in the network's loss takes it from 1.71 K to 1.60 K, and anchored to the stations it is the best model on the hottest 5% of days (1.60 K against 2.05 K for ERA5-Land).</p><p>This points towards the denser regional ARPA station networks, about ten times as many stations, as the way to separate the best models.",
"006": "A fleet of solar plants carries correlated risk. If each site's P95, its output in a bad year, is worked out on its own, the fleet's bad year is underpriced, because the same clouds cover many sites at once. This project builds the framework for measuring that shared risk, the step that has to come before simulated weather or stochastic event sets can price it.</p><p>The aim was to measure how far the weather stays correlated across 25 Spanish solar regions, what that does to the fleet's output and revenue at OMIE prices, and how ECMWF's physics (IFS) and AI (AIFS) forecast models handle it, using ERA5 solar radiation built into an Anemoi dataset.</p><p>It was found that the correlation falls to 1/e over 350 to 670 km depending on the season, so the 25 sites behave like only 3-4 independent ones. Priced at OMIE's 2023 prices, the fleet's worst 5% of days produced 16% less than independent sites would and earned about €350 against €2,500. Furthermore, it was found over 30 years of ERA5 that the fleet's 1-in-20 bad month is 10.5% below normal, four times deeper than independent sites give, which a copula event set reproduces, while forecast errors are far more local than the weather and cancel across the fleet.</p><p>This points towards pricing a solar fleet's P95 on the shared weather and the shared market, and towards repeating the analysis on CERRA at 5.5 km.",
"007": "How much weather moves both beans, arabica from Brazil and robusta from Vietnam, from an importer's point of view, with the Brazilian real stripped out first. Vietnam heat moves both beans, and the two beans spike together half the time, so buying from the other origin hedges an importer less and less when it matters. When ECMWF's seasonal forecast flagged Vietnam as unusually hot or dry, arabica rose 6.9% and robusta 5.5% over the next three months.",
"008": "The devastating storms in Chile got me interested in how Earth observation can show their impact on industrial zones. Ship traffic at the copper ports tracks Peru's official copper exports, and Sentinel-2's shortwave infrared finds heat at 24 of 30 smelters. Neither predicts the price in steady conditions, so the interesting cases are disruptions: in the July 2026 Chile storm, detection and price were days apart.",
"009": "This project measures how much the weather moves the Italian power price once gas is taken out, on real Italy North data for 2018-2026. Day by day, heat lifts power above gas. Over months the weather matters for volatility in the opposite direction to a 2026 study: months with more extreme days are calmer, because in a heatwave gas plants set the price every hour. A three-month forecast adds almost nothing.",
"010": "Inspired by Ecology for Bankers (May, Levin & Sugihara 2008): a 16-page LaTeX note deriving May's stability bound and percolation thresholds, then applying them to supply-chain risk when the Rhine runs low. A low-water month costing about 1% of German industrial output fits a network that is safe and one close to tipping, and past the threshold the average loss jumps to 38%.",
"011": "Seismology is built on signal processing, which ties it to my other projects, and earth systems are where my passion in applied mathematics lies. Southern California has about 10,000 earthquakes a year, most of them too small to feel, and under Los Angeles many are buried in traffic and other noise.</p><p>The aim was to find which denoising methods keep what a seismologist needs from a recording, the P-wave arrival time and the first motion (whether the ground moves up or down first). Filters, wavelets and a random-matrix denoiser were scored on 3,000 of the noisiest labelled recordings from the Southern California Seismic Network (Ross, Meier &amp; Hauksson, 2018), and minimum-variance stacking on a synthetic array.</p><p>It was found that the random-matrix denoiser picked 98% of arrivals only because every recording had its arrival at the same point. With the arrivals moved at random it picked 60%, against 56% with no denoising. A plain bandpass filter was the only method that helped (63%) without changing any first motions, while wavelets added about 3 dB of signal-to-noise but flipped the first motion on about one trace in fourteen.</p><p>Furthermore, it was found on the synthetic array that minimum-variance weights cancel noise shared between neighbouring sensors (13.9 dB against 10.9 dB for a plain average of 32), but only once the noise covariance is cleaned with shrinkage, from 0.2 s of noise rather than 0.8 s.",
"012": "I built this small Python library to support my other projects, since most of them involve some kind of correlation, signal processing, filtering or data assimilation. I wanted one set of tools I knew worked, so that when I code with AI agents the tools they call are always consistent and correct, and building it made me learn the mathematics behind each method.</p><p>The aim was one library for correlation measures, estimators for messy data, factor removal, random-matrix cleaning and array stacking, each tested against a known answer or an established library. There are 59 tests, and the rank correlations and Ledoit-Wolf shrinkage match SciPy and scikit-learn.</p><p>On ten years of daily returns for 39 US stocks, it was found that removing the market raises the effective number of independent bets from about 7 to 15, and the sectors appear as blocks once the matrix is ordered by clustering. Furthermore, it was found that cleaning a one-year matrix closes only a small part of the gap between the risk a minimum-variance portfolio predicts and the risk it delivers, with realised risk 1.41 to 1.48 times the prediction for every method.</p><p>The library is the shared engine of the Spanish solar portfolio (006) and the seismic denoiser (011).",
"013": "This project tests the standard producer hedges against one real shock: Russia's 2010 heatwave and export ban, when European wheat rose 39%. In hindsight the producer did best unhedged, but judged on 3 May, before the event, the ranking reverses. An Italian miller on the other side saved €53 a tonne by buying futures. The same weather shock in another country was a windfall for one side and a loss for the other.",
"014": "A learning project. I learned option pricing from Mark Joshi's <em>The Concepts and Practice of Mathematical Finance</em>, before and during my time as a quantitative analyst at Wieldmore, where I dealt with many kinds of options beyond European ones, Asian options among them. It tied in well with the PDEs and numerical methods from my physics degree. My main interest is commodities, and an Asian option pays on the average price over a period, which is how commodity buyers usually hedge, because they buy steadily rather than on one day.</p><p>The aim was to price and hedge an Asian option on coffee, cocoa and sugar futures with volatility that follows the calendar, building every price at least two independent ways: Monte Carlo with a control variate, moment matching, a finite-difference solver and Večeř's one-dimensional PDE.</p><p>It was found that the three methods agree, with Večeř's PDE within one Monte Carlo standard error (about 0.0003 on a price near 8), and that the geometric Asian as a control variate cuts the Monte Carlo variance by 1,100 to 7,200 times. Furthermore, the simulations reproduce well-known results. The Asian's delta fades as the average locks in, but most of its hedging risk comes just before and at the start of averaging, and ignoring seasonal volatility changes the price (by about 1% for coffee) but not how well the hedge works.</p><p>The same pricing and delta hedging carry into the wheat hedging project (013).",
"015": "Undergraduate numerical simulation work in C++: Laplace's equation solved on the unit square by successive over-relaxation (SOR), which pushes each update past the neighbour average so it converges faster. I later ported the solver to Python with Numba to study the compute cost against the relaxation factor and grid size, and applied the same SOR machinery to the Black-Scholes equation.",
"017": "Undergraduate numerical simulation work in C++. A fourth-order Runge-Kutta integrator, written by hand, solves dx/dt = (t - 2)²(x + 1) and is checked against the exact solution. Its error falls as the fourth power of the step size. A boundary-value problem is then solved by the shooting method, bisecting on the starting slope.",
"016": "Undergraduate Monte Carlo work in C++: the Potts model sampled with the Metropolis algorithm on a 24 x 24 lattice. For q = 3 the transition is continuous, near β ≈ 1.04-1.06, close to the exact value ln(1 + √3) ≈ 1.005. For q = 5 it is first order and much sharper. The same model, scaled up and given biological rules, became the coral reef project (003).",
}


def thumb(folder, name):
    """Centre-crop to 8:5 and save at 2x the 96 x 60 display size."""
    src = os.path.join(ROOT, folder, "figures", name)
    im = Image.open(src)
    im.seek(min(getattr(im, "n_frames", 1) - 1, 40))  # a frame part-way into an animation
    im = im.convert("RGB")
    w, h = im.size
    tw, th = (w, round(w * 5 / 8)) if w * 5 / 8 <= h else (round(h * 8 / 5), h)
    l, t = (w - tw) // 2, (h - th) // 2
    out = im.crop((l, t, l + tw, t + th)).resize((192, 120), Image.LANCZOS)
    key = folder.split("/")[-1]
    os.makedirs(THUMBS, exist_ok=True)
    out.save(os.path.join(THUMBS, key + ".png"), optimize=True)
    return f"images/thumbs/{key}.png"


CSS = """
  <style>
    /* ---- redesign ---- */
    .wrap { max-width: 1120px; }
    .project-head { grid-template-columns: 96px 3rem minmax(0, 1fr) 8.5rem 6.5rem; align-items: center; padding: .7rem 0; }
    .thumb { width: 96px; height: 60px; object-fit: cover; display: block; border: 1px solid var(--rule);
             filter: grayscale(.35) contrast(.95); transition: filter .2s; }
    .project-head:hover .thumb, .project.open .thumb { filter: none; }
    .project-head:hover .title { text-decoration: underline; text-underline-offset: 4px; }
    .project-head::after { content: "+"; grid-column: 5; justify-self: end; display: none; }
    .detail { display: block; padding: .5rem 0 2rem 0; }
    .detail .text { display: flow-root; }
    .detail .credit { font-size: .74rem; line-height: 1.55; }
    .detail .gh, .detail .view-more { font-size: .74rem; }
    .infull { max-width: 46rem; margin: 0 0 2rem; }
    .infull p { font-size: .86rem; line-height: 1.7; margin: 0 0 .8rem; }
    .infull ul.abs { font-size: .86rem; line-height: 1.65; margin: 0 0 .9rem; padding-left: 1.1rem; }
    .infull ul.abs li { margin: 0 0 .4rem; }
    .infull p.eq { font-family: 'Cambria Math', 'STIX Two Math', Georgia, serif; font-size: .95rem; text-align: center; margin: .2rem 0 1rem; }
    .step p + p, .step ul + p, .step p + ul { margin-top: .6rem; }
    .step ul { margin: 0; padding-left: 1.1rem; font-size: .84rem; line-height: 1.6; }
    .step ul li { margin: 0 0 .3rem; }
    .step .figs { display: flex; flex-direction: column; gap: 1.4rem; min-width: 0; }
    .gallery { float: right; width: 52%; margin: .25rem 0 1rem 2.25rem;
               display: grid; grid-template-columns: 1fr 1fr; gap: .6rem; }
    .detail.flip .gallery { float: left; margin: .25rem 2.25rem 1rem 0; }
    .gallery figure { margin: 0; background: #fff; border: 1px solid var(--rule); }
    .gallery .big { grid-column: 1 / -1; }
    .gallery img { width: 100%; display: block; object-fit: contain; aspect-ratio: auto; }
    .gallery .big img { max-height: 460px; }
    .gallery .small img { height: 200px; }
    @media (max-width: 760px) {
      .project-head { grid-template-columns: 64px minmax(0, 1fr); gap: .75rem; }
      .project-head .num, .project-head .tag, .project-head .status { display: none; }
      .thumb { width: 64px; height: 40px; }
      .gallery, .detail.flip .gallery { float: none; width: 100%; margin: 0 0 1.25rem; }
    }
  </style>
</head>"""

STRIP = re.compile(r'\n  <style>\n    /\* ---- redesign ---- \*/.*?</style>\n</head>', re.S)


def apply(page, base):
    """Restyle a built page. base is the prefix the project images are served from."""
    page = STRIP.sub("</head>", page)
    page = page.replace(".project:hover .project-head,\n    .project.open .project-head", ".project.open .project-head")
    page = page.replace(".project:hover .more,\n    .project.open .more", ".project.open .more")
    page = page.replace(".project:has(:focus-visible) .more { grid-template-rows: 1fr; }", "")
    items = re.split(r'(?=    <li class="project")', page)
    out = [items[0]]
    for k, block in enumerate(items[1:]):
        m = re.search(r'class="gh" href="[^"]*?(?:tree/main/|\.\./)([^"]+?)(?:/README\.md)?"', block)
        folder = m.group(1) if m else None
        if folder in PICK and 'class="gallery"' not in block:
            tsrc, gal = PICK[folder]
            t = thumb(folder, tsrc)
            block = block.replace('<span class="num">', f'<img class="thumb" src="{t}" alt="" loading="lazy"><span class="num">', 1)
            figs = "".join(
                f'<figure class="{"big" if i == 0 else "small"}"><img src="{base}{folder}/figures/{g}" alt="" loading="lazy"></figure>'
                for i, g in enumerate(gal))
            block = re.sub(r'(<div class="detail">.*?</div>\s*)<figure>.*?</figure>', lambda mm: mm.group(1), block, count=1, flags=re.S)
            block = block.replace('<div class="text">', f'<div class="text"><div class="gallery">{figs}</div>', 1)
            num = re.search(r'<span class="num">(\d+)', block).group(1)
            tm = re.search(r'(<div class="text">)(.*?)(<p class="(?:credit|stack)")', block, re.S)
            if num in SUMMARY and tm:
                paras = re.findall(r'<p(?: class="eq")?>.*?</p>|<ul class="abs">.*?</ul>', tm.group(2), re.S)
                body = tm.group(2)
                for para in paras:
                    body = body.replace(para, "", 1)
                body = body.replace('</div>', '</div><p>' + SUMMARY[num] + '</p>', 1)
                block = block[:tm.start(2)] + body + block[tm.end(2):]
                ext = re.search(r'aria-controls="(ext-\d+)"', block).group(1)
                block = block.replace(f'<div class="ext" id="{ext}" hidden>',
                                      f'<div class="ext" id="{ext}" hidden>\n          <div class="infull">' + "".join(paras) + '</div>', 1)
                block = block.replace('>+ view more<', '>+ full write-up, method and results<', 1)
            if k % 2:
                block = block.replace('<div class="detail">', '<div class="detail flip">', 1)
        out.append(block)
    return CSS.join("".join(out).split("</head>", 1))
