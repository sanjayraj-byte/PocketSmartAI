const tabs = [...document.querySelectorAll(".tab")];
const form = document.querySelector("#planner-form");
const fields = document.querySelector("#dynamic-fields");
const title = document.querySelector("#form-title");
const imageField = document.querySelector("#image-field");
const submitBtn = document.querySelector("#submit-btn");
const emptyState = document.querySelector("#empty-state");
const results = document.querySelector("#results");
const resultBadge = document.querySelector("#result-badge");
let planner = "home";

const config = {
 home: {title:"Home budget planner", button:"Build my budget plan", fields:`
  <div class="field-grid">
   <div><label for="room">Room type</label><select id="room" name="room"><option>Living room</option><option>Bedroom</option><option>Kitchen</option><option>Dining room</option><option>Whole home</option></select></div>
   <div><label for="home-size">Room size</label><select id="home-size" name="home_size"><option>Not specified</option><option>Small</option><option>Medium</option><option>Large</option></select></div>
   <div class="full"><label for="items">Items to include</label><input id="items" name="items" placeholder="e.g. 2 fans, 4 lights, sofa, curtains"></div>
  </div>`},
 party: {title:"Party budget planner", button:"Plan my event", fields:`
  <div class="field-grid">
   <div><label for="event-type">Event type</label><select id="event-type" name="event_type"><option>Birthday</option><option>Wedding</option><option>Family gathering</option><option>Corporate event</option><option>Other celebration</option></select></div>
   <div><label for="guests">Number of guests</label><input id="guests" name="guests" type="number" min="1" max="100000" value="20" required></div>
   <div class="full"><label for="venue">Venue details</label><input id="venue" name="venue" placeholder="e.g. home, community hall, outdoor"></div>
   <div class="full"><label for="date">Event date (optional)</label><input id="date" name="event_date" type="date"></div>
  </div>`},
 jewelry: {title:"Jewelry budget planner", button:"Find my style", fields:`
  <div class="field-grid">
   <div><label for="occasion">Occasion</label><select id="occasion" name="occasion"><option>Wedding</option><option>Party</option><option>Daily wear</option><option>Festival</option><option>Gift</option></select></div>
   <div><label for="style">Jewelry style</label><select id="style" name="style"><option>Elegant</option><option>Traditional</option><option>Minimal</option><option>Modern</option><option>Statement</option></select></div>
   <div class="full"><label for="material">Preferred material</label><select id="material" name="material"><option>No preference</option><option>Gold-tone</option><option>Silver-tone</option><option>Imitation jewelry</option><option>Gold</option><option>Silver</option><option>Artificial / fashion jewelry</option></select></div>
  </div>`}
};

function selectPlanner(next) {
 planner = next;
 tabs.forEach(t => t.classList.toggle("active", t.dataset.planner === planner));
 title.textContent = config[planner].title;
 fields.innerHTML = config[planner].fields;
 submitBtn.querySelector("span:first-child").textContent = config[planner].button;
 imageField.classList.toggle("hidden", planner !== "jewelry");
 document.querySelector("#image").value = "";
}
tabs.forEach(t => t.addEventListener("click", () => selectPlanner(t.dataset.planner)));
document.querySelectorAll("[data-budget]").forEach(b => b.addEventListener("click", () => {
 document.querySelector("#budget").value = b.dataset.budget;
}));
function escapeHTML(value) {
 return String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function money(amount, currency) {
 try { return new Intl.NumberFormat("en-IN",{style:"currency",currency:currency,maximumFractionDigits:0}).format(amount); }
 catch { return `${currency} ${Number(amount).toLocaleString()}`; }
}
function renderPlan(data) {
 emptyState.classList.add("hidden");
 results.classList.remove("hidden");
 resultBadge.textContent = data.source === "gemini" ? "Gemini AI plan" : "Demo plan";
 let html = `<div class="summary"><div class="optional">TOTAL BUDGET</div><div class="amount">${money(data.budget,data.currency)}</div><p>${escapeHTML(data.summary || "Your budget plan is ready.")}</p></div>`;
 if (data.allocations?.length) {
  html += `<h3>Budget allocation</h3>`;
  data.allocations.forEach(a => {
   const pct = Math.max(0,Math.min(100,Number(a.share_percent ?? (Number(a.amount)/Number(data.budget)*100))));
   html += `<div class="allocation"><div class="allocation-head"><strong>${escapeHTML(a.category)}</strong><span>${money(a.amount,data.currency)} · ${Math.round(pct)}%</span></div><div class="bar"><i style="width:${pct}%"></i></div><p>${escapeHTML(a.suggestion || "")}</p></div>`;
  });
 }
 if (data.recommendations?.length) {
  html += `<h3>Ideas to explore</h3>`;
  data.recommendations.forEach(r => {
   html += `<article class="rec-card"><div class="rec-top"><strong>${escapeHTML(r.title || "Recommendation")}</strong><span class="platform">${escapeHTML(r.platform || "Suggested option")}</span></div><p>${escapeHTML(r.reason || "")}${r.estimated_price != null ? " Estimated: "+escapeHTML(money(r.estimated_price,data.currency))+"." : ""}</p><p><b>Search:</b> ${escapeHTML(r.search_query || r.title || "")}</p>${r.url && /^https?:\/\//i.test(r.url) ? `<a href="${escapeHTML(r.url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a>` : ""}</article>`;
  });
 }
 if (data.image_observation) html += `<h3>Image notes</h3><p class="optional">${escapeHTML(data.image_observation)}</p>`;
 if (data.tips?.length) html += `<h3>Before you decide</h3><ul class="tips">${data.tips.map(t=>`<li>${escapeHTML(t)}</li>`).join("")}</ul>`;
 results.innerHTML = html;
}
form.addEventListener("submit", async e => {
 e.preventDefault();
 const budget = Number(document.querySelector("#budget").value);
 if (!Number.isFinite(budget) || budget <= 0) { alert("Enter a budget greater than zero."); return; }
 const fd = new FormData();
 fd.append("budget", String(budget));
 fd.append("currency", document.querySelector("#currency").value);
 fd.append("location", document.querySelector("#location").value || "India");
 fd.append("preferences", document.querySelector("#preferences").value);
 const details = {};
 fields.querySelectorAll("input,select,textarea").forEach(el => {
  if (el.name && el.value) details[el.name] = el.value;
 });
 fd.append("details", JSON.stringify(details));
 const img = document.querySelector("#image").files[0];
 if (planner === "jewelry" && img) fd.append("image", img);
 submitBtn.disabled = true;
 submitBtn.querySelector("span:first-child").textContent = "Creating your plan…";
 resultBadge.textContent = "Working…";
 try {
  const response = await fetch(`/api/generate-${planner}`, {method:"POST",body:fd});
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Request failed. Check the server terminal.");
  renderPlan(payload);
 } catch(err) {
  resultBadge.textContent = "Could not generate";
  emptyState.classList.remove("hidden");
  alert(err.message || "Could not connect to PocketSmart AI. Is the server running?");
 } finally {
  submitBtn.disabled = false;
  submitBtn.querySelector("span:first-child").textContent = config[planner].button;
 }
});
selectPlanner("home");
