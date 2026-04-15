SELECT
    gender,
    ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
GROUP BY gender
ORDER BY total_revenue DESC;
