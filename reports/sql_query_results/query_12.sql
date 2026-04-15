SELECT
    location,
    COUNT(*) AS total_customers,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(AVG(purchase_amount), 2) AS average_purchase_amount,
    ROUND(100.0 * AVG(CASE WHEN subscription_status = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS subscriber_share_pct
FROM customer
GROUP BY location
HAVING COUNT(*) >= 50
ORDER BY total_revenue DESC, subscriber_share_pct DESC
LIMIT 10;
