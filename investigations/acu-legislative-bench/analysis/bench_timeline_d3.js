// Static D3 rendering code for the ACU bench interactive timeline.
// Loaded unchanged by derived/bench_timeline_chart.html; the DATA global is
// injected by build_bench_timeline_d3.py above this script.
// Layout mirrors bench_timeline_chart.png: one lane per member, y-offsets
// within a lane for contributions (center) / press (above) / lobbying
// (below) / bill-intro (bottom).
//
// Two interaction layers on top of the static PNG design (both compose --
// a layer toggled off stays off regardless of lane highlight, and a dimmed
// lane stays dimmed regardless of which layers are visible):
//  1. Layer toggles: click a legend swatch to show/hide that marker type.
//  2. Lane highlight: hover a lane (or its label) to dim the rest; click to
//     pin the highlight so it survives moving the mouse to read tooltips;
//     click the same lane again (or the pinned pill's "x") to release.

(function () {
  const members = DATA.members;
  const colors = DATA.colors;

  const margin = { top: 20, right: 30, bottom: 30, left: 90 };
  const laneHeight = 74;
  const width = 1400;
  const height = members.length * laneHeight;

  const parseDate = d3.timeParse("%Y-%m-%d");
  const xDomainStart = parseDate("2021-10-01");
  const xDomainEnd = parseDate("2026-06-01");

  // --- interaction state ---
  const layerVisible = { contrib: true, press: true, lobbying: true, bill: true };
  let pinnedLane = null;   // member name, or null
  let hoveredLane = null;  // member name, or null (only matters when nothing pinned)

  const svg = d3.select("#chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom + 24);

  // diagonal-stripe pattern for lobbying-filing quarters -- one pattern per
  // member (in that member's own color) so the stripe reads as a subtle
  // texture on the lane's own background during that quarter, not a
  // separate foreground element. Quarterly filings are a coarser grain than
  // a point-in-time event, so "this quarter has a matching filing" is
  // background texture, not a marker competing with contributions/press/
  // bill-intro for attention.
  const defs = svg.append("defs");
  members.forEach(m => {
    defs.append("pattern")
      .attr("id", `lobbying-stripes-${m}`)
      .attr("width", 8).attr("height", 8)
      .attr("patternUnits", "userSpaceOnUse")
      .attr("patternTransform", "rotate(45)")
      .append("rect")
      .attr("width", 4).attr("height", 8)
      .attr("fill", colors[m])
      .attr("opacity", 0.16);
  });
  // neutral gray version for the legend swatch only (not tied to one member)
  defs.append("pattern")
    .attr("id", "lobbying-stripes-legend")
    .attr("width", 8).attr("height", 8)
    .attr("patternUnits", "userSpaceOnUse")
    .attr("patternTransform", "rotate(45)")
    .append("rect")
    .attr("width", 4).attr("height", 8)
    .attr("fill", "#555")
    .attr("opacity", 0.5);

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top + 24})`);

  const x = d3.scaleTime().domain([xDomainStart, xDomainEnd]).range([0, width]);
  const yLane = d3.scaleBand().domain(members).range([0, height]).padding(0);

  function laneY(member, offsetFrac) {
    return yLane(member) + yLane.bandwidth() / 2 + offsetFrac * yLane.bandwidth();
  }

  function activeLane() {
    return pinnedLane || hoveredLane;
  }

  // lane background bands (also the lane-highlight hit target)
  const laneBg = g.selectAll(".lane-bg")
    .data(members)
    .join("rect")
    .attr("class", "lane-bg")
    .attr("x", 0)
    .attr("y", d => yLane(d))
    .attr("width", width)
    .attr("height", yLane.bandwidth())
    .attr("fill", d => colors[d])
    .attr("opacity", 0.05)
    .style("cursor", "pointer")
    .on("mouseenter", (event, d) => { hoveredLane = d; refreshLaneOpacity(); })
    .on("mouseleave", () => { hoveredLane = null; refreshLaneOpacity(); })
    .on("click", (event, d) => {
      pinnedLane = (pinnedLane === d) ? null : d;
      refreshLaneOpacity();
      updatePinPill();
    });

  // --- lobbying filings: quarter-wide background texture, full lane height ---
  // a filing covers its whole quarter, not a point in time, so this shades
  // the LANE ITSELF (full height, member's own color, low opacity) across
  // that quarter's x-range, rather than drawing a separate foreground
  // element -- it reads as "this quarter had a matching filing," sitting
  // behind gridlines/axis/point-in-time markers, not competing with them.
  // One band per (member, quarter); when >1 bill is matched in the same
  // quarter (e.g. Barr: TABS + UDAAP), the tooltip lists all of them.
  // Rendered right after laneBg (before gridlines/axis/markers) so it never
  // paints over anything that should read as foreground. Because it's
  // full-lane-height, it sits on top of laneBg and would otherwise swallow
  // the lane-highlight hover/click -- so it also re-fires those same
  // handlers (in addition to its own tooltip) rather than blocking them.
  const MIN_BAND_W = 2; // px floor so a single-quarter band stays hoverable at full zoom-out

  const lobbyingSel = g.selectAll(".lobbying-band")
    .data(DATA.lobbying)
    .join("rect")
    .attr("class", "lobbying-band")
    .attr("x", d => x(parseDate(d.quarter_start)))
    .attr("width", d => Math.max(MIN_BAND_W, x(parseDate(d.quarter_end)) - x(parseDate(d.quarter_start))))
    .attr("y", d => yLane(d.member))
    .attr("height", d => yLane.bandwidth())
    .attr("fill", d => `url(#lobbying-stripes-${d.member})`)
    .style("cursor", "pointer")
    .on("mouseenter", (event, d) => { hoveredLane = d.member; refreshLaneOpacity(); })
    .on("mouseleave", () => { hoveredLane = null; refreshLaneOpacity(); })
    .on("click", (event, d) => {
      pinnedLane = (pinnedLane === d.member) ? null : d.member;
      refreshLaneOpacity();
      updatePinPill();
    })
    .on("mouseover", (event, d) => {
      const billsHtml = d.bills.map(b => `
        <div style="margin-top:4px;">
          <b style="font-size:11px;">${b.bill_label}</b><br>
          <i>&ldquo;${b.excerpt.slice(0, 150)}${b.excerpt.length > 150 ? "&hellip;" : ""}&rdquo;</i><br>
          <a href="${b.lda_url}" target="_blank">View LDA filing &rarr;</a>
        </div>`).join("");
      showTooltip(`<b>${d.member} &mdash; ACU lobbying, ${d.filing_period.split(" (")[0]} ${d.filing_year}</b>
        ${d.bills.length} bill${d.bills.length > 1 ? "s" : ""} named this quarter:
        ${billsHtml}`, event);
    })
    .on("mouseout", () => {
      hideTooltip();
    });

  // x axis (years)
  g.append("g")
    .attr("class", "axis")
    .attr("transform", `translate(0,${height})`)
    .call(d3.axisBottom(x).ticks(d3.timeYear.every(1)).tickFormat(d3.timeFormat("%Y")));

  // gridlines
  g.append("g")
    .attr("class", "grid")
    .selectAll("line")
    .data(x.ticks(d3.timeYear.every(1)))
    .join("line")
    .attr("x1", d => x(d)).attr("x2", d => x(d))
    .attr("y1", 0).attr("y2", height)
    .attr("stroke", "#ddd").attr("stroke-width", 0.8)
    .attr("pointer-events", "none");

  // y axis (member labels) -- also clickable/hoverable, same as lane-bg
  g.selectAll(".lane-label")
    .data(members)
    .join("text")
    .attr("class", "lane-label")
    .attr("x", -10)
    .attr("y", d => yLane(d) + yLane.bandwidth() / 2)
    .attr("text-anchor", "end")
    .attr("dominant-baseline", "middle")
    .style("cursor", "pointer")
    .text(d => d)
    .on("mouseenter", (event, d) => { hoveredLane = d; refreshLaneOpacity(); })
    .on("mouseleave", () => { hoveredLane = null; refreshLaneOpacity(); })
    .on("click", (event, d) => {
      pinnedLane = (pinnedLane === d) ? null : d;
      refreshLaneOpacity();
      updatePinPill();
    });

  // pinned-lane indicator pill, top-right of the chart
  const pinPill = svg.append("g")
    .attr("class", "pin-pill")
    .attr("transform", `translate(${margin.left + width - 170}, 4)`)
    .style("display", "none")
    .style("cursor", "pointer")
    .on("click", () => { pinnedLane = null; refreshLaneOpacity(); updatePinPill(); });
  pinPill.append("rect").attr("width", 170).attr("height", 20).attr("rx", 10)
    .attr("fill", "#333").attr("opacity", 0.85);
  const pinPillText = pinPill.append("text")
    .attr("x", 10).attr("y", 14).attr("fill", "white").attr("font-size", 11);

  function updatePinPill() {
    if (pinnedLane) {
      pinPillText.text(`Pinned: ${pinnedLane} (click to release)`);
      pinPill.style("display", null);
    } else {
      pinPill.style("display", "none");
    }
  }

  // tooltip -- pointer-events:auto (see CSS) so a link inside it (LDA
  // filing, press URL, congress.gov) is actually clickable. That means
  // moving the mouse from the marker into the tooltip briefly leaves BOTH
  // elements for a frame, which would instantly hide it before the click
  // lands -- so hideTooltip is debounced on a short timer, and the
  // tooltip's own mouseenter cancels a pending hide (mouseleave re-arms
  // it), so it only disappears once the mouse has actually left both the
  // marker and the tooltip.
  const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .on("mouseenter", cancelHideTooltip)
    .on("mouseleave", hideTooltip);

  let hideTimer = null;

  function showTooltip(html, event) {
    cancelHideTooltip();
    tooltip.html(html)
      .style("left", (event.pageX + 14) + "px")
      .style("top", (event.pageY + 10) + "px")
      .style("opacity", 1);
  }
  function hideTooltip() {
    cancelHideTooltip();
    hideTimer = setTimeout(() => tooltip.style("opacity", 0), 150);
  }
  function cancelHideTooltip() {
    if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  }

  const fmtDate = d3.timeFormat("%b %-d, %Y");
  const fmtMoney = d3.format(",.0f");

  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  const rngSeeded = mulberry32(42);

  // --- bill introductions: stars, offset -0.40 ---
  const starSymbol = d3.symbol().type(d3.symbolStar).size(140);

  const billSel = g.selectAll(".bill-star")
    .data(DATA.billDates)
    .join("path")
    .attr("class", "bill-star")
    .attr("d", starSymbol)
    .attr("transform", d => `translate(${x(parseDate(d.date))},${laneY(d.member, -0.40)})`)
    .attr("fill", "#b8860b")
    .attr("stroke", "#333")
    .attr("stroke-width", 0.5)
    .style("cursor", "pointer")
    .on("mouseover", (event, d) => {
      d3.select(event.currentTarget).attr("stroke-width", 1.5);
      showTooltip(`<b>${d.member} &mdash; Bill introduced</b>
        ${d.bill_number}<br>
        <i>${d.official_title}</i><br>
        ${d.purpose ? d.purpose + "<br>" : ""}
        Sponsor: ${d.sponsor}<br>
        Introduced: ${fmtDate(parseDate(d.date))}<br>
        Latest action (${d.latest_action_date}): ${d.latest_action_text}<br>
        <a href="${d.url}" target="_blank">View on Congress.gov &rarr;</a>`, event);
    })
    .on("mouseout", (event) => {
      d3.select(event.currentTarget).attr("stroke-width", 0.5);
      hideTooltip();
    });

  // --- contributions: circles, center lane, sized by sqrt(amount) ---
  const rMax = d3.max(DATA.contributions, d => Math.abs(d.amount));
  const rScale = d3.scaleSqrt().domain([0, rMax]).range([2, 13]);

  const contribSel = g.selectAll(".contrib-dot")
    .data(DATA.contributions)
    .join("circle")
    .attr("class", "contrib-dot")
    .attr("cx", d => x(parseDate(d.date)))
    .attr("cy", d => laneY(d.member, (rngSeeded() - 0.5) * 0.24))
    .attr("r", d => rScale(Math.abs(d.amount)))
    .attr("fill", d => colors[d.member])
    .style("cursor", "pointer")
    .on("mouseover", (event, d) => {
      d3.select(event.currentTarget).attr("stroke", "#333").attr("stroke-width", 1);
      showTooltip(`<b>${d.member} &mdash; ACU contribution</b>
        $${fmtMoney(d.amount)}<br>
        From: ${d.payer}<br>
        To: ${d.payee}<br>
        Date: ${fmtDate(parseDate(d.date))}<br>
        <a href="${d.lda_url}" target="_blank">View LD-203 filing &rarr;</a>`, event);
    })
    .on("mouseout", (event) => {
      d3.select(event.currentTarget).attr("stroke", "none");
      hideTooltip();
    });

  // --- press mentions: triangles, offset +0.34 ---
  const triSymbol = d3.symbol().type(d3.symbolTriangle).size(110);

  const pressSel = g.selectAll(".press-mark")
    .data(DATA.press)
    .join("path")
    .attr("class", "press-mark")
    .attr("d", triSymbol)
    .attr("transform", d => `translate(${x(parseDate(d.date))},${laneY(d.member, 0.34)})`)
    .attr("fill", d => colors[d.member])
    .attr("stroke", "#333")
    .attr("stroke-width", 0.6)
    .style("cursor", "pointer")
    .on("mouseover", (event, d) => {
      d3.select(event.currentTarget).attr("stroke-width", 2);
      showTooltip(`<b>${d.member} &mdash; ACU press mention</b>
        <i>${d.title}</i><br>
        ${d.chamber} release, ${fmtDate(parseDate(d.date))}<br>
        <a href="${d.url}" target="_blank">Read release &rarr;</a>`, event);
    })
    .on("mouseout", (event) => {
      d3.select(event.currentTarget).attr("stroke-width", 0.6);
      hideTooltip();
    });

  // --- combined opacity: layer-toggle (on/off) x lane-highlight (dim/full) ---
  // base opacities per layer, matching the original static design
  const BASE_OPACITY = { contrib: 0.45, press: 0.95, lobbying: 1, bill: 0.9 };
  const DIMMED_OPACITY = { contrib: 0.06, press: 0.12, lobbying: 0.08, bill: 0.12 };

  function laneOpacityFor(member) {
    const active = activeLane();
    if (!active) return 1;
    return member === active ? 1 : 0.35;
  }

  function refreshLaneOpacity() {
    const active = activeLane();

    laneBg.attr("opacity", d => (active ? (d === active ? 0.10 : 0.03) : 0.05));
    g.selectAll(".lane-label").attr("opacity", d => (active ? (d === active ? 1 : 0.35) : 1))
      .attr("font-weight", d => (active && d === active ? 700 : 400));

    contribSel.attr("opacity", d => layerVisible.contrib
      ? BASE_OPACITY.contrib * laneOpacityFor(d.member) : 0)
      .attr("pointer-events", d => (layerVisible.contrib ? null : "none"));
    pressSel.attr("opacity", d => layerVisible.press
      ? BASE_OPACITY.press * laneOpacityFor(d.member) : 0)
      .attr("pointer-events", d => (layerVisible.press ? null : "none"));
    lobbyingSel.attr("opacity", d => layerVisible.lobbying
      ? BASE_OPACITY.lobbying * laneOpacityFor(d.member) : 0)
      .attr("pointer-events", d => (layerVisible.lobbying ? null : "none"));
    billSel.attr("opacity", d => layerVisible.bill
      ? BASE_OPACITY.bill * laneOpacityFor(d.member) : 0)
      .attr("pointer-events", d => (layerVisible.bill ? null : "none"));
  }

  // --- legend, doubling as layer-visibility toggles ---
  const legend = svg.append("g")
    .attr("class", "legend")
    .attr("transform", `translate(${margin.left + 10}, 6)`);

  const legendItems = [
    { key: "contrib", label: "Contribution (size = $ amount)", type: "circle", color: "#888" },
    { key: "press", label: "ACU press mention", type: "triangle", color: "#888" },
    { key: "lobbying", label: "ACU lobbying filing naming member's bill (quarter span)", type: "band", color: "#555" },
    { key: "bill", label: "Bill introduced (Congress.gov)", type: "star", color: "#b8860b" },
  ];

  let lx = 0;
  legendItems.forEach(item => {
    const item_g = legend.append("g")
      .attr("class", "legend-item")
      .attr("transform", `translate(${lx},0)`)
      .style("cursor", "pointer")
      .on("click", () => {
        layerVisible[item.key] = !layerVisible[item.key];
        item_g.attr("opacity", layerVisible[item.key] ? 1 : 0.35);
        refreshLaneOpacity();
      });

    // invisible hit-rect widens the click target to the full label
    const itemWidth = item.label.length * 6.3 + 34;
    item_g.append("rect").attr("x", -4).attr("y", -10).attr("width", itemWidth)
      .attr("height", 20).attr("fill", "transparent");

    if (item.type === "circle") {
      item_g.append("circle").attr("cx", 6).attr("cy", 0).attr("r", 5).attr("fill", item.color).attr("opacity", 0.5);
    } else if (item.type === "triangle") {
      item_g.append("path").attr("d", d3.symbol().type(d3.symbolTriangle).size(80))
        .attr("transform", "translate(6,0)").attr("fill", item.color);
    } else if (item.type === "band") {
      item_g.append("rect").attr("x", 0).attr("y", -6).attr("width", 12).attr("height", 12)
        .attr("fill", "url(#lobbying-stripes-legend)");
    } else if (item.type === "star") {
      item_g.append("path").attr("d", d3.symbol().type(d3.symbolStar).size(90))
        .attr("transform", "translate(6,0)").attr("fill", item.color).attr("stroke", "#333").attr("stroke-width", 0.5);
    }
    item_g.append("text").attr("x", 16).attr("y", 4).text(item.label);
    lx += itemWidth + 6;
  });

  legend.append("text")
    .attr("x", lx + 10).attr("y", 4)
    .attr("fill", "#888").attr("font-size", 10).attr("font-style", "italic")
    .text("(click to toggle · hover/click a lane to highlight)");

  refreshLaneOpacity();
  updatePinPill();
})();
