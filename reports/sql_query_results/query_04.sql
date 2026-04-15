SELECT
    shipping_type,
    ROUND(AVG(purchase_amount), 2) AS average_purchase_amount
FROM customer
WHERE shipping_type IN ('Standard', 'Express')
GROUP BY shipping_type
ORDER BY average_purchase_amount DESC;
