# Technical Interview Questions & Model Answers
## Business / Product / Data Analyst Complete Guide

*28 technical questions with detailed answers, SQL examples, and step-by-step arithmetic*

---

## A. SQL & Data Modeling (10 Questions)

### 1. Monthly Cohort Retention Analysis

**Question:** Write a query to compute monthly cohort retention (cohort by first purchase month — percent retained in month 0..N).

**Why they ask:** Tests ability to write windowed aggregations, group-by time bucketing, and produce cohort matrices.

**Expected Answer:**
Describe approach: define cohorts by first purchase month, track activity in subsequent periods, calculate retention percentages.

**SQL Solution:**
```sql
WITH first_purchase AS (
  SELECT customer_id,
         date_trunc('month', MIN(order_date)) AS cohort_month
  FROM orders
  GROUP BY customer_id
),
orders_month AS (
  SELECT customer_id,
         date_trunc('month', order_date) AS order_month
  FROM orders
)
SELECT
  fp.cohort_month,
  EXTRACT(month FROM age(om.order_month, fp.cohort_month))::int AS month_index,
  COUNT(DISTINCT om.customer_id) AS active_customers_in_month,
  COUNT(DISTINCT fp.customer_id) AS cohort_size,
  (COUNT(DISTINCT om.customer_id)::numeric / COUNT(DISTINCT fp.customer_id))::numeric(5,4) AS retention_rate
FROM first_purchase fp
JOIN orders_month om
  ON fp.customer_id = om.customer_id
GROUP BY fp.cohort_month, month_index
ORDER BY fp.cohort_month, month_index;
```

**Key Points to Mention:**
- Use `date_trunc` to align months
- Handle customers with no repeat orders (month_index = 0 only)
- Consider censoring for partial months (cohorts near present date)
- Large tables: ensure `orders` has index on `customer_id` and `order_date` for performance

---

### 2. RFM Scoring Implementation

**Question:** How do you compute RFM scores in SQL and produce top-10% VIP segment?

**Why they ask:** Tests understanding of customer segmentation and quantile-based scoring.

**Expected Answer:**
Compute recency, frequency, monetary per customer; use `ntile()` or quantiles for scoring.

**SQL Solution:**
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
SELECT
  customer_id,
  recency_days,
  frequency,
  monetary,
  ntile(5) OVER (ORDER BY recency_days ASC)    AS r_score,  -- ASC because lower recency = better
  ntile(5) OVER (ORDER BY frequency DESC)      AS f_score,
  ntile(5) OVER (ORDER BY monetary DESC)       AS m_score
FROM rfm;
```

**What to say in interview:** Explain how you map scores to segments (e.g., `555` = VIP). Emphasize checking distribution — if data is skewed use custom thresholds instead of uniform quintiles.

---

### 3. Active Users with Zero Purchases

**Question:** Given two tables `users` and `events`, how do you find users who were active this month but had zero purchases last 6 months?

**Why they ask:** Tests joins, null handling, and filtering logic.

**SQL Solution:**
```sql
WITH purchases_6m AS (
  SELECT user_id, COUNT(*) AS purchases
  FROM orders
  WHERE order_date >= CURRENT_DATE - INTERVAL '6 months'
  GROUP BY user_id
)
SELECT u.user_id
FROM users u
JOIN events e ON u.user_id = e.user_id
LEFT JOIN purchases_6m p ON u.user_id = p.user_id
WHERE date_trunc('month', e.event_time) = date_trunc('month', CURRENT_DATE) -- active this month
  AND COALESCE(p.purchases, 0) = 0
GROUP BY u.user_id;
```

**Testing point:** joins, null handling, `COALESCE`, grouping semantics.

---

### 4. Join Types Explanation

**Question:** Explain different join types and when to use each.

**Expected Answer:**
- **INNER JOIN** — return rows present in both sets (use for matching events)
- **LEFT JOIN** — all left rows, matching right rows or NULL (use to keep all customers)
- **RIGHT JOIN** — symmetrical of LEFT (rarely used)
- **FULL OUTER JOIN** — union of both with NULLs for non-matches
- **SEMI JOIN** or `EXISTS` — check existence without duplicating columns
- **ANTI JOIN** (`LEFT JOIN ... WHERE right.id IS NULL` or `NOT EXISTS`) — find non-matches (e.g., churned customers)

**What interviewers listen for:** Mention performance considerations (e.g., converting `IN` with large lists to `JOIN`), and deduplication issues.

---

### 5. Query Optimization

**Question:** How to optimize a slow query on a large `orders` table?

**Expected Answer (practical checklist):**
- Check query plan (`EXPLAIN ANALYZE`)
- Add/confirm appropriate indexes (e.g., composite `(customer_id, order_date)`, or `(order_date)` for time filters)
- Replace `SELECT *` with only needed columns
- Aggregate precompute (materialized views) for expensive sums if run often
- Use partitioning (time-range partition) for very large time-series
- Ensure stats up to date, avoid functions on indexed columns in WHERE (e.g., avoid `DATE(order_date)` on indexed `order_date`)

---

### 6. Month-over-Month Growth and CAGR

**Question:** Write a SQL snippet to compute month-over-month revenue growth and CAGR over a 3-year span.

**SQL for Revenue Aggregation:**
```sql
SELECT
  date_trunc('month', order_date) AS month,
  SUM(order_value) AS revenue
FROM orders
GROUP BY 1
ORDER BY 1;
```

**CAGR Calculation (step-by-step arithmetic):**
If `beginning = 80,000` and `ending = 120,000` over `n = 3` years:

1. **Ratio** = `ending / beginning` = `120,000 ÷ 80,000 = 1.5`
2. **Compute cube root:** Using logs: `ln(1.5) ≈ 0.4054651081`. Divide by 3 → `0.4054651081 ÷ 3 = 0.1351550360`. Exponentiate → `e^0.1351550360 ≈ 1.144714242`
3. **Subtract 1** → `1.144714242 − 1 = 0.144714242`
4. **CAGR ≈ 14.471% per year**

**What interviewer expects:** Show both SQL for aggregation and correct manual arithmetic for CAGR.

---

### 7. Duplicate Detection and Removal

**Question:** How would you detect duplicate rows and remove them safely?

**Expected Answer:**
- **Detect** with `GROUP BY`/`HAVING COUNT(*) > 1` or `ROW_NUMBER()` window to identify duplicates
- **Remove** using CTE with `ROW_NUMBER()` keeping the earliest/most complete row

**SQL Example:**
```sql
WITH duplicates AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY natural_key_columns ORDER BY created_at DESC) AS rn
  FROM orders
)
DELETE FROM orders o
USING duplicates d
WHERE o.id = d.id AND d.rn > 1;
```

**Safety:** Always backup or run SELECT first; flag duplicates, investigate cause (ETL bug).

---

### 8. Median Calculation

**Question:** How do you write a query to compute median order value (not mean)?

**SQL Solution:**
```sql
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY order_value) AS median_order_value
FROM orders
WHERE order_date BETWEEN '2025-01-01' AND '2025-06-30';
```

**Why median matters:** Less sensitive to outliers than mean.

---

### 9. Data Warehouse Schema Design

**Question:** Explain star schema vs snowflake schema. Which do you prefer and why?

**Expected Answer:**
- **Star schema:** Facts (events/transactions) connected to denormalized dimension tables — simple, fast for queries and BI
- **Snowflake:** Normalized dimensions (split further) — saves storage, but adds joins and complexity
- **Preference:** Star schema for analytics/BI (simpler, faster), use snowflake when dimensions are very wide or need normalization for data integrity

Mention indexing and columnar storage (Redshift/Snowflake) to optimize.

---

### 10. Slowly Changing Dimensions

**Question:** How to implement slowly changing dimensions (SCD) for customer attributes? Which SCD types exist?

**Expected Answer:**
- **Type 1:** Overwrite old value (no history). Use when historical values are irrelevant
- **Type 2:** Add new row with surrogate key and effective dates (preserve history). Use for critical attributes (pricing tier changes)
- **Type 3:** Add new column for previous value (partial history). Use rarely

**Implementation:** In ETL, compare incoming record to current dimension row(s); for Type 2 create new row and set `end_date` on prior row; manage surrogate keys. Mention pragmatic considerations: table size, query complexity, and maintaining foreign keys.

---

## B. Analytics & Experimentation (6 Questions)

### 11. Complete A/B Test Walkthrough

**Question:** Walk through an A/B test: sample size calculation, running the test, and interpreting results.

**Expected Answer:**
- **Define** primary metric and MDE (minimum detectable effect), significance level α (commonly 0.05) and power (commonly 0.8)
- **Sample size:** For proportions, use statistical calculator or formula
- **Run test:** Random assignment, run until min sample or time reached, avoid peeking (or use sequential testing methods)
- **Analyze:** Compute difference, standard error, z/t, p-value; present confidence intervals and practical impact on revenue
- **Decision rules:** Adopt variant if statistically significant and practically meaningful (positive ROI)

**Interviewer wants to hear:** Power/sample size calculation and practical significance (lift × traffic × AOV = revenue impact).

---

### 12. Experiment Integrity

**Question:** How do you detect snoozing/peeking problems in experiments and how to mitigate them?

**Expected Answer:**
- **Detection:** Look for fluctuating p-values and correlation between sample size/time and p-values, suspiciously many significant results after multiple looks
- **Mitigation:** Pre-register experiment, fix sample size or use sequential testing methods (e.g., O'Brien–Fleming, alpha spending, or Bayesian methods), use Bonferroni correction if many variants

---

### 13. Statistical vs Practical Significance

**Question:** Explain statistical significance vs practical significance.

**Expected Answer:**
- **Statistical significance:** Result unlikely under null (p < α) — depends on effect size, variance, and sample size
- **Practical significance:** Effect magnitude mattering to business (e.g., 0.1% lift may be statistically significant on huge N but negligible in revenue)

Always translate lift into monetary impact (visitors × lift × AOV) and consider test costs and risk.

---

### 14. Type I and Type II Errors

**Question:** What are Type I and Type II errors in experiments?

**Expected Answer:**
- **Type I (false positive):** Reject true null — probability α
- **Type II (false negative):** Fail to reject false null — probability β (power = 1 − β)

Practical answer includes choosing α & power given business cost of errors.

---

### 15. Cannibalization Testing

**Question:** How do you design a test to measure promotion cannibalization (i.e., whether discounts steal demand from other SKUs)?

**Expected Answer:**
- Use geo or user-level holdouts where some regions/users get promotion and others don't
- Measure absolute incremental revenue vs control and SKU-level substitution (decrease in other SKUs)
- Compute net incremental revenue = incremental for promoted SKU − decrease in other SKUs in same user group
- Consider time-lagged effects and control for seasonality

---

### 16. Net Revenue Retention Implementation

**Question:** Describe how to compute Net Revenue Retention (NRR) in practice and common gotchas.

**Expected Answer:**
For a cohort or month: NRR = (Starting MRR − Churned MRR + Expansion MRR) / Starting MRR

**Gotchas:**
- Exclude new customers from expansion MRR
- Treat downgrades as contraction
- Normalize for upgrades in same month
- Handle currency changes and refunds consistently

---

## C. Product Metrics & Visualization (4 Questions)

### 17. Executive Dashboard Design

**Question:** How would you build a dashboard for executive stakeholders — what metrics and charts?

**Expected Answer:**
**High-level KPIs:** Revenue (MTD/QTD/YTD), ARR/MRR, NRR, GRR, LTV:CAC, CAC, Churn

**Operational metrics:** Funnel conversion (visitors → signups → paid), cohort retention heatmap, top channels by ROAS, top products by GMV and margin

**Visuals:** KPI cards, cohort heatmap, funnel with stage conversion percentages, time-series with annotations

Also include data quality checks and variance (confidence intervals). Keep dashboards focused on 1–2 action questions per stakeholder.

---

### 18. Chart Type Selection

**Question:** How do you choose between line charts, bar charts, heatmaps, and Sankey diagrams?

**Expected Answer:**
- **Time-series** → line chart
- **Comparison across discrete categories** → bar chart
- **Two-dimensional matrix (cohort retention)** → heatmap
- **Flow analysis (conversion paths)** → Sankey

Emphasize clarity: annotate axes, avoid 3D charts, use appropriate scales (log vs linear) and order categories meaningfully.

---

### 19. DAU/MAU Stickiness

**Question:** How do you compute DAU/MAU and interpret stickiness?

**Expected Answer:**
- **DAU** = unique users who performed a key action that day
- **MAU** = unique users in 30-day window
- **Stickiness** = DAU/MAU (ratio)

**Interpretation:** Higher stickiness indicates more frequent user engagement; e.g., 20% stickiness implies average user engages ~6 days/month (approx 30 × 0.2 = 6). Explain limitations (bots, multiple accounts).

---

### 20. Uncertainty Visualization

**Question:** How to present uncertainty on a dashboard (forecast bands, CI)?

**Expected Answer:**
- Add confidence intervals or forecast bands (e.g., 80% / 95%) around trend lines
- For categorical comparisons show error bars or bootstrap-derived CI
- Always state methodology & assumptions (e.g., ARIMA forecast with seasonality), and avoid over-precision

---

## D. Data Engineering & ETL (3 Questions)

### 21. Robust ETL Pipeline Design

**Question:** Describe a robust ETL pipeline for ingesting daily orders into an analytics warehouse.

**Expected Answer:**
- **Ingestion:** Batch at fixed window or streaming via Kafka; ingest raw events to landing area (immutable)
- **Staging:** Validate/clean (schema checks, nulls, data types), deduplicate using unique constraints or de-dup keys
- **Transform:** Apply business logic, compute derived fields (AOV, status), join dimensions
- **Load:** Incremental load to fact tables via upsert or append with partitioning (e.g., by `order_date`)
- **Monitoring:** Row counts vs expected, anomaly alerts, SLA checks
- **Idempotency:** Design for re-run without duplication (use hash marks or `insert ... on conflict`)

Mention versioning, data contracts, and documentation.

---

### 22. Data Quality Assurance

**Question:** How do you ensure data quality and detect issues early?

**Expected Answer:**
- Implement automated data tests (row counts, null thresholds, referential integrity)
- Use data validators (Great Expectations or custom)
- Track monitoring dashboards for freshness, distribution changes, and schema drift
- Alert on regression tests or sudden metric shifts
- Conduct periodic reconciliation (e.g., compare warehouse revenue to accounting)

---

### 23. Event Schema Design

**Question:** How do you design event schema for analytics to avoid later problems?

**Expected Answer:**
- Use clear event naming conventions and versioning
- Include `user_id`, `anonymous_id`, `timestamp`, `event_properties` (typed)
- Keep events idempotent and include `event_id` for deduplication
- Document required vs optional properties; avoid nested or inconsistent types
- Agree on semantic definitions (e.g., "signup", "activate")

---

## E. Machine Learning & Modeling (4 Questions)

### 24. Churn Prediction Model

**Question:** You need to build a churn prediction model. What steps do you take?

**Expected Answer (end-to-end):**
1. **Define label:** What counts as churn — e.g., no activity or subscription cancel within 30/60 days
2. **Choose windows:** Prediction window and observation window (e.g., use 3 months of behavior to predict churn next 1 month)
3. **Feature engineering:** RFM features, engagement events, billing anomalies, support tickets
4. **Split data:** Chronologically (train/validation/test) to avoid leakage
5. **Models:** Logistic regression for baseline; tree-based (XGBoost/LightGBM) for performance
6. **Evaluate:** AUC, precision@k, calibration, lift charts. Choose business metric (e.g., top-decile retention improvement)
7. **Deploy:** Scoring pipeline, monitor model drift, retrain schedule

**What to mention:** Calibration and cost-sensitive decisions (false positives vs false negatives), how to measure ROI of targeted retention actions.

---

### 25. Model Evaluation Metrics

**Question:** How to evaluate a model — which metrics and why? (classification/regression)

**Expected Answer:**
**Classification:**
- ROC AUC (overall discrimination)
- Precision@k (business targeting)
- Recall (sensitivity)
- F1 (balance)
- Calibration (predicted probability vs observed)
- Use PR curve for imbalanced classes

**Regression:**
- RMSE (sensitive to outliers)
- MAE (robust)
- MAPE (percentage errors) with caveats for small denominators

**Business tie-in:** Choose metric that aligns with the downstream decision (e.g., lift in retention per targeted user).

---

### 26. Overfitting Prevention

**Question:** Explain overfitting and how to prevent it.

**Expected Answer:**
- **Overfitting** = model learns noise instead of signal; performs well on training but poorly on unseen data
- **Prevention:** Cross-validation, regularization (L1/L2), early stopping, limiting model complexity, feature selection, and use of a holdout test set

---

## F. Case Studies & Applied Problems (2 Questions + 1 Worked Case)

### 27. Onboarding Flow Measurement

**Question:** How would you measure whether a new onboarding flow improves 90-day retention?

**Expected Answer:**
- **Prefer randomized A/B test** at user-level or rollout by independent units (geos)
- **Primary metric:** 90-day retention (binary)
- **Secondary:** Activation/TTFV, conversion to paid
- **Sample size:** Calculate based on baseline 90-day retention and desired uplift
- **Analysis:** Run test until required sample reached, analyze with proportion test and compute incremental 90-day retention uplift and revenue impact

If full randomization impossible, use propensity matching and difference-in-differences but mention limitations.

---

### 28. Complete Campaign Analysis (Worked Case)

**Question:** You run a paid campaign that acquired 300 customers at $30,000 spend (CAC = $100). After 6 months, cohort data shows cumulative revenue per customer = $107.50 (6-month LTV) and gross margin = 60%. Should you scale the campaign? Show calculations and reasoning.

**Step-by-Step Analysis:**

**1. Compute gross profit per customer (6-month window):**
- 6-month LTV per customer = $107.50
- Gross margin = 60% → gross profit per customer = $107.50 × 0.6
- Calculation: `107.5 × 6 = 645.0` then divide by 10 for ×0.6 → `645 ÷ 10 = 64.5`
- **Result: $64.50 gross profit per customer over 6 months**

**2. Compare to CAC:**
- CAC = $30,000 ÷ 300 = $100.00 per customer
- Immediate (6-month) payback: gross profit − CAC = $64.50 − $100 = **−$35.50 (a loss)**

**3. Interpretation:**
At 6 months the cohort still hasn't paid back CAC on gross-profit basis. But marketing decisions should consider **lifetime** beyond 6 months.

**4. Compute break-even lifetime needed:**
- Required LTV (gross) to break even on CAC = CAC / margin = 100 ÷ 0.6 = **$166.67**
- Current 6-month revenue = $107.50 < $166.67 → need more future revenue
- **Additional revenue needed:** $166.67 − $107.50 = **$59.17**

**5. Decision Framework:**
Scale only if you expect future (post-6-month) revenue per customer to be ≥ $59.17 additional revenue.

**6. Other Considerations:**
- Channel consistency (is this campaign repeatable?)
- Ability to reduce CAC
- Margin differences by product mix
- Alternative uses of spend

**Final Recommendation:**
Do **not** scale blindly. Run experiments to improve onboarding/retention or lower CAC, and compute projected lifetime break-even before allocating more budget. Present sensitivity scenarios (e.g., if 12-month LTV increases to $200 → gross profit $120 → profitable).

---

## Interview Preparation Strategy

### How to Use This Guide

**Memorize the Structure:**
- One-line definition → approach/steps → example/code → caveats → decision criteria
- Interviewers appreciate clarity and operational judgment

**Practice Writing SQL:**
- Write SQL by hand (you may be asked to whiteboard)
- Keep code clear and index-aware

**Show Your Work:**
- When asked for numeric estimation or to compute an effect, **show arithmetic step-by-step**
- State assumptions and time windows
- Always translate metrics into business impact (dollars, % growth, time to payback)

### Role-Specific Focus Areas

**Product Analyst:**
- Focus on sections B (Analytics & Experimentation) and C (Product Metrics)
- Emphasize user behavior analysis and feature impact measurement

**Growth Analyst:**
- Emphasize sections A (SQL) and B (Analytics), especially cohort analysis and attribution
- Focus on customer acquisition and retention metrics

**Data Analyst:**
- Strong emphasis on sections A (SQL) and D (Data Engineering)
- Focus on data modeling and pipeline design

### Time Management

- **SQL Questions:** 15-20 minutes including explanation
- **Analytics Questions:** 10-15 minutes for conceptual, 20-25 for worked examples
- **Case Studies:** 25-30 minutes including calculations and recommendations

Remember: The interviewer cares more about your thought process and business judgment than perfect syntax or exact calculations.
