SELECT
    customer_lifetime_segment,
    shipping_type,
    COUNT(*) AS total_customers,
    ROUND(AVG(purchase_amount), 2) AS average_spend,
    ROUND(AVG(CAST(review_rating AS DECIMAL(10, 2))), 2) AS average_rating
FROM customer
GROUP BY customer_lifetime_segment, shipping_type
ORDER BY customer_lifetime_segment, average_spend DESC, total_customers DESC;
