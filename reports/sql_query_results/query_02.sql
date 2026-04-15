WITH average_purchase AS (
    SELECT AVG(purchase_amount) AS avg_purchase_amount
    FROM customer
)
SELECT
    c.customer_id,
    c.purchase_amount
FROM customer AS c
CROSS JOIN average_purchase AS ap
WHERE c.discount_applied = 'Yes'
  AND c.purchase_amount >= ap.avg_purchase_amount
ORDER BY c.purchase_amount DESC, c.customer_id;
