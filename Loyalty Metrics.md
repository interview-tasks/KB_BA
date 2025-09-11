# Comprehensive Loyalty Analytics Guide
## Metrics, Analysis & Implementation Framework

*20 loyalty metrics with formulas, worked examples, and SQL implementations*

**Baseline Business Metrics (Reference):**
- Annual revenue: **$120,000**
- Orders (year): **2,400** 
- Customers (total): **1,200**
- Active customers: **800**
- New customers: **300**
- AOV: **$50**
- Gross margin: **60%**

---

## Core Loyalty Metrics

### 1. RFM Analysis (Recency, Frequency, Monetary)

**Definition:** Behavioral segmentation using Recency (days since last purchase), Frequency (purchase count), and Monetary (total spend).

**Calculation Method:**
1. For each customer compute: Recency (days), Frequency (count), Monetary (sum)
2. Convert each to quantile scores 1–5, combine as RFM code (e.g., `5-4-3`)

**Worked Example - Customer A:**
- Last purchase: 12 days ago
- Purchases (12 months): 5
- Spend (12 months): $350

**Step-by-step scoring:**
1. Recency = 12 days → assuming 0–29 days = score 5 → **R = 5**
2. Frequency = 5 → top quintile → **F = 5** 
3. Monetary = $350 → top quintile → **M = 5**
4. **RFM code = 5-5-5 (VIP customer)**

**Business Value:**
- Target VIPs (555) for premium offers
- Identify at-risk high-value customers (high F/M but low R) for winback
- Use as features in churn prediction models

**Pitfalls:** Using uniform quantiles when distribution is heavy-tailed — inspect distributions and consider custom thresholds.

**SQL Implementation:**
```sql
WITH rfm AS (
  SELECT
    customer_id,
    EXTRACT(day FROM (CURRENT_DATE - MAX(order_date)))::int AS recency_days,
    COUNT(*) AS frequency,
    SUM(order_value) AS monetary
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY customer_id
)
SELECT customer_id, recency_days, frequency, monetary,
       ntile(5) OVER (ORDER BY recency_days ASC) AS r_score,
       ntile(5) OVER (ORDER BY frequency DESC)   AS f_score,
       ntile(5) OVER (ORDER BY monetary DESC)    AS m_score
FROM rfm;
```

---

### 2. Repeat Purchase Rate (RPR)

**Definition:** Share of customers who make more than one purchase in a period.

**Formula:** `RPR = Customers with >1 order ÷ Total customers in period`

**Worked Example:**
- Total customers: 1,200
- Customers with >1 purchase: 600

**Calculation:**
1. RPR = 600 ÷ 1,200 = 0.5
2. **RPR = 50%**

**Business Value:** Measures loyalty and product stickiness; raising RPR increases LTV without new acquisition costs.

**Pitfalls:** Time-window sensitivity — use rolling windows and cohort analysis.

**Action:** Implement timed re-engagement campaigns just before median repurchase time.

---

### 3. Purchase Frequency & Inter-purchase Time

**Definition:** Average number of purchases per customer and average time between purchases.

**Formulas:**
- `Purchase frequency = Total orders ÷ Unique customers`
- `Avg inter-purchase time = Window days ÷ Purchase frequency`

**Worked Example (Baseline):**
- Total orders: 2,400
- Customers: 1,200

**Calculations:**
1. Frequency = 2,400 ÷ 1,200 = **2 purchases/customer/year**
2. Inter-purchase interval = 365 ÷ 2 = **182.5 days**

**Business Value:** Informs cadence of retention messaging (e.g., reminder ~150 days if distribution skewed).

**Pitfalls:** Skewed distributions — use median inter-purchase and percentiles instead of means.

---

### 4. Customer Lifetime Value (CLV) - Loyalty View

**Definition:** Expected gross contribution from a customer across their lifetime.

**Formula:** `CLV = AOV × Purchase frequency per year × Expected lifetime (years) × Gross margin`

**Worked Example:**
- AOV: $50
- Frequency: 2 purchases/year  
- Expected lifetime: 3 years
- Gross margin: 60% (0.6)

**Step-by-step calculation:**
1. AOV × frequency = 50 × 2 = 100
2. Multiply by lifetime: 100 × 3 = 300  
3. Multiply by margin: 300 × 0.6 = 180
4. **CLV = $180 per customer (gross contribution)**

**Business Value:** Sets budget for acquisition and loyalty investment per customer; compute LTV uplift from loyalty program.

**Pitfalls:** Ignoring discounting for long horizons and customer heterogeneity — always compute cohort LTVs.

---

### 5. Cohort Retention Curves

**Definition:** For an acquisition cohort, the percent still active in each subsequent period.

**Worked Example - January Cohort:**
- Cohort size: 300 new customers
- Monthly retention: M0=100% (300), M1=60% (180), M2=50% (150), M3=45% (135)

**Calculations:**
- Month 1 retained = 300 × 0.60 = 180
- Month 2 retained = 300 × 0.50 = 150

**Business Value:** Shows when loyalty drops off and indicates where to invest in onboarding or benefits to improve retention.

**Pitfalls:** Small cohorts produce noisy retention rates.

**Action:** Segment cohorts by channel to find which acquisition source produces the most loyal customers.

---

### 6. Churn Rate & Survival Analysis

**Definition:** Proportion of customers who stop transacting in a period.

**Formula:** `Churn = Customers lost during month ÷ Customers at start of month`

**Worked Example:**
- Starting customers: 1,000
- Lost customers: 50

**Calculation:**
1. 50 ÷ 1,000 = 0.05
2. **Monthly churn = 5%**

**Business Value:** Quantifies loyalty decay; survival analysis helps forecast expected lifetime and tail behavior.

**Pitfalls:** Not distinguishing voluntary vs involuntary churn (e.g., card declines).

---

### 7. Net Promoter Score (NPS)

**Definition:** `NPS = %Promoters (9–10) − %Detractors (0–6)`

**Worked Example:**
- Survey respondents: 500 total
- Promoters: 300 (60%)
- Detractors: 100 (20%)

**Calculation:**
1. NPS = 60% − 20% = **40**

**Business Value:** Predicts referrals and loyalty; helps prioritize CX fixes. Use verbatim analysis to find root causes.

**Pitfalls:** Biased sampling and low response rates. Measure both transactional and relationship NPS.

---

### 8. Referral Rate & Viral Coefficient

**Definitions:**
- `Referral rate = Customers who referred ÷ Total customers`
- `Viral coefficient = Average invites per customer × Conversion probability of invite`

**Worked Example:**
- Total customers: 1,200
- Customers who made ≥1 referral: 120

**Calculations:**
1. Referral rate = 120 ÷ 1,200 = 0.10 = **10%**

**Viral Coefficient Example:**
- Average invites: 2
- Invite conversion: 10% (0.1)
- Viral coefficient = 2 × 0.1 = **0.2** (<1 → no viral growth)

**Business Value:** Measures word-of-mouth loyalty and helps forecast organic growth potential.

**Pitfalls:** Easy to measure invites but harder to link true conversion attributable to referral.

---

## Loyalty Program Specific Metrics

### 9. Enrollment & Participation Rates

**Definitions:**
- `Enrollment rate = Customers enrolled ÷ Eligible customers`
- `Participation rate = Active participants ÷ Enrolled customers`

**Worked Example:**
- Eligible customers: 1,000
- Enrolled: 400
- Active participants (earned/redeemed in 6 months): 300

**Calculations:**
1. Enrollment rate = 400 ÷ 1,000 = **40%**
2. Participation rate = 300 ÷ 400 = **75%**

**Business Value:** Enrollment shows program appeal; participation shows ongoing engagement and likely loyalty.

**Pitfalls:** Enrollment doesn't equal engagement — track both metrics.

**SQL Implementation:**
```sql
-- Enrollment Rate
SELECT COUNT(DISTINCT customer_id) AS enrolled
FROM loyalty_enrollments
WHERE enrolled_date <= CURRENT_DATE;

-- Participation (earned or redeemed in last 6 months)
SELECT COUNT(DISTINCT customer_id) AS participants
FROM loyalty_activity
WHERE activity_date >= CURRENT_DATE - INTERVAL '6 months';
```

---

### 10. Points Issuance vs Redemption & Breakage Rate

**Definitions:**
- `Breakage = (Issued − Redeemed) ÷ Issued`

**Worked Example:**
- Points issued (monetary equivalent): $100,000
- Points redeemed: $60,000

**Calculation:**
1. Breakage = (100,000 − 60,000) ÷ 100,000 = 40,000 ÷ 100,000 = 0.4
2. **Breakage rate = 40%**

**Business Value:** High breakage improves short-term margin but risks member dissatisfaction if points expire too quickly.

**Pitfalls:** Regulatory/accounting recognition — point liabilities must be reserved accurately.

---

### 11. Redemption Rate & Velocity

**Definitions:**
- `Redemption rate = Redeemed points ÷ Issued points`
- `Redemption velocity = Average time between earning and redemption (days)`

**Worked Example:**
- Redemption rate = 60,000 ÷ 100,000 = **60%**
- Average earn-to-redeem time = **120 days**

**Business Value:** Balance between reward attractiveness and cost control; velocity informs program liquidity.

---

### 12. Incremental LTV from Loyalty Program

**Definition:** Incremental lifetime value (ΔLTV) attributable to loyalty program participation.

**Measurement:** Best via randomized enrollment (A/B) or propensity-score matched holdouts.

**Worked Example:**
- Enrolled cohort 6-month LTV: $150 revenue
- Non-enrolled cohort 6-month LTV: $107.50 revenue
- Gross margin: 60%

**Step-by-step calculation:**
1. Enrolled gross profit: 150 × 0.6 = (150 × 6) ÷ 10 = 900 ÷ 10 = **$90**
2. Non-enrolled gross profit: 107.5 × 0.6 = **$64.50**
3. Incremental gross profit: 90 − 64.5 = **$25.50**

If program cost per customer = $10, then net incremental profit = 25.50 − 10 = **$15.50**

**Business Value:** Direct ROI of loyalty program and justification for scaling.

**Pitfall:** Selection bias — high-value customers more likely to enroll; use randomized tests.

---

### 13. Loyalty Program ROI & Payback

**Formula:** `Program ROI = (Incremental gross profit − Program cost) ÷ Program cost`

**Worked Example:**
- Enrolled customers: 10,000
- Incremental gross profit per customer: $25.50
- Total program cost: $100,000

**Calculations:**
1. Total incremental = 10,000 × 25.5 = **$255,000**
2. Net gain = 255,000 − 100,000 = **$155,000**
3. ROI = 155,000 ÷ 100,000 = 1.55 = **155% ROI**

**Business Value:** Shows whether loyalty program is financially sensible to run or scale.

**Pitfalls:** Double-counting incremental revenue — always require holdout for accurate measurement.

---

### 14. Tier Migration Rate

**Definition:** Percent of members moving up (or down) between program tiers in a period.

**Formula:** `Migration rate (up) = Members who moved to higher tier ÷ Members eligible`

**Worked Example:**
- Total enrolled members: 400
- Members who moved Silver to Gold: 80

**Calculation:**
1. Migration up rate = 80 ÷ 400 = 0.2 = **20%**

**Business Value:** Indicates whether program encourages increased spend/engagement; positive sign if migration aligns with higher LTV.

**Pitfalls:** If migration driven by discounts rather than sustained value, check gross profit per tier.

---

### 15. Share of Wallet (SOW)

**Definition:** Proportion of customer's total category spend that goes to your brand.

**Formula:** `SOW = Customer spend with you ÷ Customer total category spend`

**Worked Example:**
- Customer total category spend: $1,000/year
- Customer spend with you: $100/year

**Calculation:**
1. SOW = 100 ÷ 1,000 = 0.10 = **10%**

**Business Value:** Measures room to grow via loyalty — high SOW means fewer upsell opportunities, low SOW means potential to grow share.

**Pitfalls:** Accurately estimating total category spend often requires surveys or external data.

---

### 16. Customer Health Score

**Definition:** Weighted index combining engagement, recency, purchase frequency, NPS, and support interactions.

**Example Formula:**
`Health = 0.35 × normalized_recency + 0.25 × normalized_frequency + 0.20 × NPS_scaled + 0.20 × engagement_score`

**Worked Example - One Customer:**
- Normalized scores: recency 0.8, frequency 0.6, NPS scaled 0.7, engagement 0.5

**Step-by-step calculation:**
1. 0.35 × 0.8 = **0.28**
2. 0.25 × 0.6 = **0.15**  
3. 0.20 × 0.7 = **0.14**
4. 0.20 × 0.5 = **0.10**
5. Sum = 0.28 + 0.15 + 0.14 + 0.10 = **0.67**
6. **Health score = 0.67** (on 0–1 scale)

**Business Value:** Prioritize outreach for "yellow" customers to push into "green" VIP tier; combine with propensity models.

---

### 17. Redemption Source Attribution

**Definition:** Allocate redemption conversions to prior touchpoints (campaigns/emails) to estimate which channels trigger loyalty behavior.

**Method:** Multi-touch attribution on redemption events, or last-touch within window (e.g., last 30 days).

**Business Value:** Invest in channels that not only acquire but also trigger loyalty behaviors (e.g., email nudges vs broad display ads).

**Pitfall:** Attribution windows and cross-device tracking complexity.

---

### 18. Loyalty Cohort LTV by Enrollment Date

**Definition:** Track cohorts based on enrollment date (or tier upgrade date) to compute LTV and churn conditional on program status.

**Use Case:** Compare LTV of customers who enrolled in program month X vs control.

**Business Value:** Quantifies program efficacy and informs optimization strategies.

---

### 19. Program Leakage & Fraud Rate

**Definition:** Share of points or discounts redeemed in abusive/fraudulent ways.

**Measurement:** `Fraud rate = Flagged transactions ÷ Total redemptions`

**Business Value:** Operational control — ensure program integrity and control cost overruns.

**Pitfall:** False positives in fraud detection hurting genuine customers — tune thresholds carefully.

---

### 20. Loyalty Incremental ROAS

**Definition:** Incremental revenue per dollar spent on loyalty incentives; measured using randomized enrollment or holdouts.

**Worked Example:**
- Program spending: $100k
- Incremental revenue: $255k (from earlier example)
- Incremental ROAS = 255,000 ÷ 100,000 = **2.55**

**Business Value:** Helps quantify marketing efficiency of loyalty vs pure acquisition.

---

## Implementation Framework

### Recommended Experiments

1. **Always measure incrementality with holdouts** — enroll randomly to avoid selection bias when estimating uplift
2. **Segmented cohort analysis** — compute cohort LTV for enrolled vs non-enrolled by acquisition channel
3. **Bandit experiments for rewards** — test reward sizes with multi-armed bandit to optimize ROI
4. **Tier design testing** — A/B test tier thresholds to find sweet spot for motivating behavior
5. **Real-time monitoring** — maintain dashboards for enrollment, issuance, redemptions, breakage, and fraud

### Essential SQL Queries

**Enrollment Rate:**
```sql
SELECT
  COUNT(DISTINCT customer_id) AS enrolled,
  (COUNT(DISTINCT customer_id)::numeric / 
   (SELECT COUNT(DISTINCT customer_id) FROM customers WHERE eligible = true)) AS enrollment_rate
FROM loyalty_enrollments
WHERE enrolled_date BETWEEN '2025-01-01' AND '2025-12-31';
```

**Redemption Rate:**
```sql
SELECT
  SUM(redeemed_value) AS redeemed_value,
  SUM(issued_value) AS issued_value,
  (SUM(redeemed_value) / NULLIF(SUM(issued_value),0)) AS redemption_rate
FROM loyalty_ledger
WHERE activity_date BETWEEN '2025-01-01' AND '2025-12-31';
```

**Incremental LTV Comparison:**
```sql
WITH enrolled AS (
  SELECT customer_id, SUM(order_value) AS revenue
  FROM orders
  WHERE customer_id IN (
    SELECT customer_id FROM loyalty_enrollments 
    WHERE enrolled_date BETWEEN '2025-01-01' AND '2025-06-30'
  )
  GROUP BY customer_id
),
control AS (
  SELECT customer_id, SUM(order_value) AS revenue
  FROM orders
  WHERE customer_id NOT IN (SELECT customer_id FROM loyalty_enrollments)
  GROUP BY customer_id
)
SELECT
  (SELECT AVG(revenue) FROM enrolled) AS avg_enrolled_revenue,
  (SELECT AVG(revenue) FROM control) AS avg_control_revenue,
  (SELECT AVG(revenue) FROM enrolled) - (SELECT AVG(revenue) FROM control) AS incremental_revenue;
```

### Operational Decision Triggers

| Metric | Threshold | Action Required |
|--------|-----------|----------------|
| **Enrollment rate** | <20% | Rework program messaging or simplify enrollment |
| **Participation rate** | <40% | Program may be too complex or rewards irrelevant |
| **Breakage rate** | >60% | Points expire too quickly or hard to redeem |
| **Tier migration** | <5% YoY | Tier thresholds too high or benefits not motivating |
| **Incremental LTV** | < Incentive cost | Program losing money; redesign benefits or targeting |

### Implementation Checklist

**✅ Design Phase:**
- [ ] Design experiments (randomized holdouts) for major program changes
- [ ] Define business metrics (incremental LTV, participation, redemption rate, breakage)
- [ ] Set attribution windows and measurement methodology

**✅ Technical Setup:**
- [ ] Instrument events cleanly (`loyalty_enroll`, `points_issued`, `points_redeemed`, `tier_change`)
- [ ] Include `event_id` for deduplication
- [ ] Maintain finance reconciliation from loyalty ledger to P&L

**✅ Optimization:**
- [ ] Segment & personalize using RFM + propensity models
- [ ] Apply right incentives to right customers
- [ ] Monitor and iterate based on performance data

**✅ Monitoring:**
- [ ] Real-time dashboards for key metrics
- [ ] Financial reconciliation (reserve for points outstanding)
- [ ] Regular cohort analysis and program ROI assessment

---

## Next Steps

This guide provides the foundation for measuring and optimizing loyalty programs. Consider these follow-up activities:

1. **Excel/Google Sheets calculator** with pre-filled baseline numbers for quick metric computation
2. **Experiment design template** for measuring incremental LTV from tiered loyalty programs
3. **Visual dashboard examples** (cohort heatmaps, RFM treemaps) for executive presentations

The key to successful loyalty analytics is consistent measurement, rigorous experimentation, and focus on incremental business impact rather than vanity metrics.
