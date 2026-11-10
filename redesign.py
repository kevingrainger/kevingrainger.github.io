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
    "003-po-valley-downscaling": ("cover.png", ["cover.png", "real/fig8_physics_informed_real.png", "fig4_footprints.png"]),
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
"001": "My undergraduate capstone at Trinity College Dublin, supervised by Prof. Cormac McGuinness: modelling the spin and energy gap of metal-porphyrin nano-networks with density functional theory, in FHI-aims. The bridge between units decides whether a bare chain is magnetic. One oxygen bound to the metal overrides the bridge, leaving a single local spin and a gap the bridge still sets. A spin that switches when a molecule binds is the mechanism a chemical sensor needs.",
"002": "A rebuilt agent-based model of Xylella spreading through an olive grove, carried from tree to tree by spittlebugs, light enough to be run and tuned many more times. Outbreaks are usually fatal: 39 of 40 take the whole grove. Below roughly 16% infection per visit outbreaks die out, and with trees 6 to 8 cells apart they stop taking the grove. None of the felling patterns slowed the spread.",
"003": "This project models a reef much as physics models a magnet: a Potts-style lattice of healthy coral, bleached coral, bare rock and seaweed. Reefs get stuck: once heat kills enough coral, cooling the water back down does not bring it back. Fitted by simulation-based inference to 65 AIMS surveys of Scott Reef in 2016, two very different reefs reproduce the surveys equally well, and they tip at +1.1 to 1.7 °C.",
"004": "Kéfi et al.'s probabilistic cellular automaton for drylands, the same neighbour coupling as the coral reef's Potts model. Recovering from desert takes much more rainfall than the collapse did, and the patch structure warns of decline well before cover falls. Driven by real rain at two field sites and 223 grid sites, and played beside forty years of Landsat and Sentinel-2, rain alone cannot explain which land re-greened: land use decides more of it.",
"005": "In my work in quantitative climate risk at Wieldmore I became interested in regional climate models. This is a calibrated model of daily maximum temperature for the Po Valley that matches every station reading exactly, compared with kriging, a U-Net and a physics-informed U-Net. On the real data every regional model beats ERA5-Land by about 0.3 K, and anchored to the stations the physics-informed network is the best model on the hottest days.",
"006": "A fleet of solar plants carries correlated risk. If each site's P95 is worked out on its own, the fleet's bad year is underpriced, because the same clouds cover many sites at once. Across 25 Spanish solar regions the weather stays correlated over 350 to 670 km, so the portfolio behaves like only 3-4 independent sites (on the hourly clear-sky index), and its 1-in-20 bad month is about four times deeper than independent sites would give.",
"007": "How much weather moves both beans, arabica from Brazil and robusta from Vietnam, from an importer's point of view, with the Brazilian real stripped out first. Vietnam heat moves both beans, and the two beans spike together half the time, so buying from the other origin hedges an importer less and less when it matters. When ECMWF's seasonal forecast flagged Vietnam as unusually hot or dry, arabica rose 6.9% and robusta 5.5% over the next three months.",
"008": "The devastating storms in Chile got me interested in how Earth observation can show their impact on industrial zones. Ship traffic at the copper ports tracks Peru's official copper exports, and Sentinel-2's shortwave infrared finds heat at 24 of 30 smelters. Neither predicts the price in steady conditions, so the interesting cases are disruptions: in the July 2026 Chile storm, detection and price were days apart.",
"009": "This project measures how much the weather moves the Italian power price once gas is taken out, on real Italy North data for 2018-2026. Day by day, heat lifts power above gas. Over months the weather matters for volatility in the opposite direction to a 2026 study: months with more extreme days are calmer, because in a heatwave gas plants set the price every hour. A three-month forecast adds almost nothing.",
"010": "Inspired by Ecology for Bankers (May, Levin & Sugihara 2008): a 16-page LaTeX note deriving May's stability bound and percolation thresholds, then applying them to supply-chain risk when the Rhine runs low. A low-water month costing about 1% of German industrial output fits a network that is safe and one close to tipping, and past the threshold the average loss jumps to 38%.",
"011": "Small earthquakes under Los Angeles are often buried in traffic and other noise. On 3,000 of the noisiest recordings from the Southern California Seismic Network I tested which denoising methods keep the P-wave arrival time and first motion. Random matrix theory only looked best because every arrival sat at the same point in the window. A plain bandpass filter was the only method that helped without changing any first motions.",
"012": "A small Python library I built to support these projects, so that when I code with AI agents, the tools they call are always consistent and correct. It covers correlation measures, estimators for messy data, factor removal, random-matrix cleaning and array stacking, and it is tested against SciPy and scikit-learn (59 tests).",
"013": "This project tests the standard producer hedges against one real shock: Russia's 2010 heatwave and export ban, when European wheat rose 39%. In hindsight the producer did best unhedged, but judged on 3 May, before the event, the ranking reverses. An Italian miller on the other side saved €53 a tonne by buying futures. The same weather shock in another country was a windfall for one side and a loss for the other.",
"014": "A learning project, from Mark Joshi's The Concepts and Practice of Mathematical Finance. My main interest is commodities, so this is the pricing groundwork for them: an Asian option pays on the average price over a period, which is how commodity buyers usually hedge. Prices are built three independent ways that check each other, and run on coffee, cocoa and sugar with seasonal volatility.",
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
                paras = re.findall(r'<p>.*?</p>', tm.group(2), re.S)
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
