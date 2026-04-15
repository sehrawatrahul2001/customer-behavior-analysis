WITH customer_segments AS (
    SELECT
        customer_id,
        previous_purchases,
        CASE
            WHEN previous_purchases = 1 THEN 'New'
            WHEN previous_purchases BETWEEN 2 AND 10 THEN 'Returning'
            ELSE 'Loyal'
        END AS customer_segment
    FROM customer
)
SELECT
    customer_segment,
    COUNT(*) AS number_of_customers
FROM customer_segments
GROUP BY customer_segment
ORDER BY CASE customer_segment
    WHEN 'New' THEN 1
    WHEN 'Returning' THEN 2
    ELSE 3
END;
