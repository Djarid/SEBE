# H200 Cluster Rack: Compute-to-Cooling Energy Ratio

## Key Figures

| Cooling Method | Annualised PUE | Cooling as % of IT Load | Compute:Cooling Ratio |
|---|---|---|---|
| Air-cooled | 1.3–1.8 | 30–50% | ~2:1 to 3:1 |
| Direct-to-chip liquid | 1.1–1.15 | 10–15% | ~7:1 |
| Immersion (oil/two-phase) | 1.03–1.05 | 3–5% | ~20:1 to 33:1 |

## Caveats

- **These are annualised averages.** Seasonal variation can swing PUE by 0.1–0.3 points at individual facilities. Winter quarters consistently outperform summer. [Google Data Centers, PUE reporting](https://datacenters.google/efficiency/)
- **Climate matters.** A facility in Miami may report PUE 1.8 while one in Alaska achieves 1.7, despite the Miami site being more efficient relative to its conditions. [Wikipedia: Power Usage Effectiveness](https://en.wikipedia.org/wiki/Power_usage_effectiveness)
- **Cooling can consume up to 50% of total facility power** in air-cooled environments. [AirSys North America](https://airsysnorthamerica.com/how-does-your-cooling-system-affect-data-center-pue/)
- **Peak summer in warm climates can push air-cooled ratios toward 1:1** (cooling energy ≈ IT load), due to degraded chiller COP as ambient temperature rises and the thermodynamic lift increases.
- **Air-cooled fan parasitic load alone can consume 15–25% of total DC power** at H200 rack densities. [Walmate Thermal: H200 Immersion Cooling Guide](https://walmatethermal.com/nvidia-h200-immersion-cooling-solution/)

## H200-Specific Thermal Context

- Single H200 GPU TDP: **700W**. Eight-GPU DGX H200 node: **~10.2 kW**. Full rack (8 nodes): **~82 kW**. [Uvation](https://uvation.com/articles/nvidia-dgx-h200-power-consumption-what-you-absolutely-must-know), [Sunbird DCIM](https://www.sunbirddcim.com/blog/nvidia-h200-power-requirements-can-your-racks-support-them)
- Immersion-cooled H200 deployments (e.g. Firmus/KenFa, 3000 units) achieved **PUE ~1.145** with GPUs held below 68°C. [KenFa Tech](https://www.kenfatech.com/nvidia-h200-gpu-server-immersion-oil-cooling-solution/)
- Best-case immersion PUE of **~1.03** is achievable but represents optimal conditions. [Walmate Thermal](https://walmatethermal.com/nvidia-h200-immersion-cooling-solution/)

## Normalised Practical Estimate

For a **typical modern H200 deployment using liquid cooling in a temperate climate**, a realistic annual ratio is approximately **5:1** (compute:cooling), corresponding to PUE ~1.2. Under peak summer load in a warm region with air cooling, this can degrade to **2:1 or worse**. Headline PUE figures of 1.03–1.1 represent best-case, not normalised, conditions.

---

*Sources accessed March 2026. PUE figures are facility-level metrics inclusive of all overhead (cooling, power distribution, lighting), not cooling-only.*
