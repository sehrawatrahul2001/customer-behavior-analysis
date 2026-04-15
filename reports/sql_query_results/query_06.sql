SELECT
    item_purchased,
    ROUND(100.0 * AVG(CASE WHEN discount_applied = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS discount_rate_pct
FROM customer
GROUP BY item_purchased
ORDER BY discount_rate_pct DESC, item_purchased
LIMIT 5;
