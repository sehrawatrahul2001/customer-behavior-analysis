SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(AVG(purchase_amount), 2) AS average_order_value
FROM customer
GROUP BY payment_method
ORDER BY total_revenue DESC, average_order_value DESC;
