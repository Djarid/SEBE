---
layout: default
title: Documents
description: "SEBE policy documents, models and analysis"
permalink: /docs/
---

<h1 class="prose" style="font-family: var(--serif); font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">Documents</h1>

<p style="color: var(--muted); margin-bottom: 1.5rem;">All SEBE documents are open source under CC-BY 4.0. Use them, adapt them, argue with them.</p>

<div class="doc-filter" role="navigation" aria-label="Filter documents">
  <button class="doc-filter-pill active" data-filter="all">All</button>
  <button class="doc-filter-pill" data-filter="policy">Policy</button>
  <button class="doc-filter-pill" data-filter="model">Models & Evidence</button>
  <button class="doc-filter-pill" data-filter="analysis">Analysis</button>
</div>

<h2 class="doc-group-heading" data-group="policy">Policy</h2>
<ul class="doc-list" data-group="policy">
  <li data-tags="policy accessible">
    <a href="{{ '/docs/SEBE_summary.html' | relative_url }}">Tax Robots, Fund People</a> <span class="post-tags"><span class="post-tag post-tag-accessible">ACCESSIBLE</span></span>
    <p class="doc-desc">Four-page overview: the problem, the mechanism, the revenue, the ask.</p>
  </li>
  <li data-tags="policy intermediate">
    <a href="{{ '/docs/green_party_submission.html' | relative_url }}">SEBE: Green Party Policy Submission</a> <span class="post-tags"><span class="post-tag post-tag-intermediate">INTERMEDIATE</span></span>
    <p class="doc-desc">Policy submission to PDC and Economy PWG. Three-framing structure: present harms, trajectory, desired outcome. MMT-framed.</p>
  </li>
  <li data-tags="policy advanced">
    <a href="{{ '/docs/academic_brief.html' | relative_url }}">Infrastructure-Based Taxation for the Post-Employment Economy</a> <span class="post-tags"><span class="post-tag post-tag-advanced">ADVANCED</span></span>
    <p class="doc-desc">Full academic analysis for think tanks and researchers. Technical feasibility, rate derivation, research agenda.</p>
  </li>
  <li data-tags="policy advanced">
    <a href="{{ '/docs/academic_brief_mmt.html' | relative_url }}">Inflation Control for the Post-Employment Economy</a> <span class="post-tags"><span class="post-tag post-tag-advanced">ADVANCED</span></span>
    <p class="doc-desc">MMT-framed analysis. SEBE as inflation control instrument, anchor migration from labour to energy, self-balancing fiscal design.</p>
  </li>
  <li data-tags="policy accessible">
    <a href="{{ '/docs/public_explainer.html' | relative_url }}">Tax Robots, Fund People</a> <span class="post-tags"><span class="post-tag post-tag-accessible">ACCESSIBLE</span></span>
    <p class="doc-desc">Plain language guide. No jargon. What it is, who pays, what you get.</p>
  </li>
  <li data-tags="policy advanced">
    <a href="{{ '/docs/green_party_submission_appendix_a.html' | relative_url }}">Appendix A: Metering, Enforcement and Billing</a> <span class="post-tags"><span class="post-tag post-tag-advanced">ADVANCED</span></span>
    <p class="doc-desc">Technical appendix to the policy submission. How SEE and DCD are metered using existing infrastructure, enforced at physical chokepoints, and billed monthly.</p>
  </li>
</ul>

<h2 class="doc-group-heading" data-group="model">Models & Evidence</h2>
<ul class="doc-list" data-group="model">
  <li data-tags="model advanced">
    <a href="{{ '/docs/revenue_model.html' | relative_url }}">SEBE Revenue Model</a> <span class="post-tags"><span class="post-tag post-tag-advanced">ADVANCED</span></span>
    <p class="doc-desc">Source of truth for all SEBE revenue figures. First-principles derivation from DESNZ and Ofcom data.</p>
  </li>
  <li data-tags="model intermediate">
    <a href="{{ '/docs/cost_model.html' | relative_url }}">SEBE Cost Model</a> <span class="post-tags"><span class="post-tag post-tag-intermediate">INTERMEDIATE</span></span>
    <p class="doc-desc">SEBE revenue in context: scale relative to existing taxes, what it could replace, what it could fund.</p>
  </li>
  <li data-tags="model intermediate">
    <a href="{{ '/docs/distribution_model.html' | relative_url }}">SEBE Distribution Model</a> <span class="post-tags"><span class="post-tag post-tag-intermediate">INTERMEDIATE</span></span>
    <p class="doc-desc">Illustrative two-stage UBI to Universal Living Income transition. Full costing and sensitivity analysis.</p>
  </li>
</ul>

<h2 class="doc-group-heading" data-group="analysis">Analysis</h2>
<ul class="doc-list" data-group="analysis">
  <li data-tags="analysis intermediate">
    <a href="{{ '/docs/brookings_rebuttal.html' | relative_url }}">Why Brookings Gets AI Taxation Wrong</a> <span class="post-tags"><span class="post-tag post-tag-intermediate">INTERMEDIATE</span></span>
    <p class="doc-desc">Detailed response to Korinek and Lockwood's AI taxation framework (January 2026).</p>
  </li>
  <li data-tags="analysis advanced">
    <a href="{{ '/docs/automation_risk.html' | relative_url }}">The Asymmetry of Automation Risk</a> <span class="post-tags"><span class="post-tag post-tag-advanced">ADVANCED</span></span>
    <p class="doc-desc">Six automation waves, four structural breaks, one asymmetric risk. MMT framing: withdrawal capacity, bathtub model, sectoral balances, EC661 alignment.</p>
  </li>
  <li data-tags="analysis intermediate">
    <a href="{{ '/docs/automation_risk_orthodox.html' | relative_url }}">The Asymmetry of Automation Risk (Orthodox Framing)</a> <span class="post-tags"><span class="post-tag post-tag-intermediate">INTERMEDIATE</span></span>
    <p class="doc-desc">Orthodox variant. Same historical evidence, framed through revenue and tax base erosion rather than MMT withdrawal capacity.</p>
  </li>
  <li data-tags="analysis advanced">
    <a href="{{ '/docs/global_transition.html' | relative_url }}">Strategic Analysis: Global Order in Transition</a> <span class="post-tags"><span class="post-tag post-tag-advanced">ADVANCED</span></span>
    <p class="doc-desc">Strategic analysis of dollar-system erosion, with UK implications and four trajectory scenarios.</p>
  </li>
  <li data-tags="analysis intermediate">
    <a href="{{ '/docs/agentic_fluency_trap.html' | relative_url }}">The Agentic Fluency Trap</a> <span class="post-tags"><span class="post-tag post-tag-intermediate">INTERMEDIATE</span></span>
    <p class="doc-desc">Why AI doesn't need to improve for displacement to accelerate. The compounding fluency curve and METR time horizon data.</p>
  </li>
</ul>

<script>
document.querySelectorAll('.doc-filter-pill').forEach(function(pill) {
  pill.addEventListener('click', function() {
    var filter = this.dataset.filter;
    document.querySelectorAll('.doc-filter-pill').forEach(function(p) {
      p.classList.remove('active');
    });
    this.classList.add('active');
    document.querySelectorAll('.doc-group-heading, .doc-list').forEach(function(el) {
      if (filter === 'all' || el.dataset.group === filter) {
        el.style.display = '';
      } else {
        el.style.display = 'none';
      }
    });
  });
});
</script>
