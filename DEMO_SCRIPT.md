# 3-Minute Hackathon Demo Script: SocialPulse

**Audience Intelligence & Timeline Analysis Engine**  
**Presenter Flow & Screen-by-Screen Walkthrough**

---

### [0:00 - 0:30] Introduction & Problem Hook
- **Speaker**: "In today’s hyper-connected landscape, social media analytics tools show vanity metrics—raw follower counts and simple positive/negative percentages. They miss the real intelligence: emotional nuance, sarcastic backlash, code-mixed multilingual sentiment, and how influence actually cascades across communities.
- **Action**: Open browser to `http://localhost:8000/`.
- **Speaker**: "This is **SocialPulse**—a full-stack audience intelligence platform that ingests raw multi-platform feeds and ties follower emotion, aggregate privacy-safe demographics, rising trends with 72-hour forecasts, and influence networks to a single unified timeline."

---

### [0:30 - 1:15] Overview & Multi-Dimensional Sentiment Explorer
- **Action**: Highlight the Overview KPI cards (Total Posts: 380, Anonymized Users, Peak Viral Topic: `#AIRevolution`).
- **Speaker**: "Notice our privacy-by-design indicator: user IDs are irreversibly salted with SHA-256 before storage. Now, let’s switch to the **Sentiment Explorer**."
- **Action**: Click on the **Sentiment Explorer** tab. Hover over the 8-class emotion stacked area chart.
- **Speaker**: "Instead of binary sentiment, we classify posts into 8 fine-grained emotional dimensions: joy, excitement, anger, anxiety, sadness, support, opposition, and neutral. Look at this spike: our engine natively handles Hinglish code-mixed text (*'Bhai AI wrapper bana kar valuation maang rahe hain, reality check kab aayega?'*) and detects subtle sarcasm, correctly flipping sarcastic praise into negative opposition."
- **Action**: Filter by "Sarcasm" or "Anger" to show post drill-down cards with polarity scores and engagement counts.

---

### [1:15 - 1:50] Demographics with $k$-Anonymity & Rising Trend Forecasting
- **Action**: Click the **Demographics** tab. Point out the verified $k$-Anonymity badge ($k \ge 20$).
- **Speaker**: "Unlike invasive surveillance tools, SocialPulse enforces strict $k$-anonymity. Any cohort smaller than 20 individuals is automatically suppressed or aggregated. We expose aggregate age brackets, country/state geography, and professional clusters without ever storing individual-level demographic profiles."
- **Action**: Switch to **Trends & Forecasts** tab.
- **Speaker**: "Next: trend forecasting. We don't just count posts; we compute **TrendScore** as Velocity × Acceleration × Unique User Spread. Selecting `#AIRevolution` renders our Holt-Winters forecasting model with 24-to-72 hour projection curves and shaded 80% and 95% uncertainty cones."

---

### [1:50 - 2:40] Network Topology, Louvain Communities & Cascade Simulator
- **Action**: Switch to the **Network & Cascade** tab.
- **Speaker**: "Here is our Network Topology engine, built on NetworkX. Nodes are sized by PageRank centrality and colored by their Louvain community partition. The amber-ringed nodes represent **Bridge Nodes**—influential connectors bridging distinct clusters, like CleanTech bridging AI and Sustainability."
- **Action**: Press the **Play** button on the Information Cascade Simulator. Observe the animation slider progressing through steps 1 to 8.
- **Speaker**: "Watch the cascade player: as breaking news spreads, SocialPulse animates the time-sliced diffusion of ideas across communities, showing step-by-step infection rates, cumulative reach, and shifting dominant emotions."

---

### [2:40 - 3:00] Data Sources, Docker & Conclusion
- **Action**: Navigate to **Data Sources** tab to show live connector health cards and worker throughput metrics.
- **Speaker**: "SocialPulse features a pluggable connector architecture for Telegram, X, Reddit, and YouTube. Best of all, it ships with a zero-credential Replay Connector and Docker Compose for instant one-command deployment on any machine. Thank you!"
