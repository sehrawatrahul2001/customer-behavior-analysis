SELECT
    age_group,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(100.0 * SUM(purchase_amount) / SUM(SUM(purchase_amount)) OVER (), 2) AS revenue_contribution_pct
FROM customer
GROUP BY age_group
ORDER BY total_revenue DESC;
