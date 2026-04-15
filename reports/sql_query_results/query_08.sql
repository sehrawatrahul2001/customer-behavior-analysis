WITH ranked_products AS (
    SELECT
        category,
        item_purchased,
        COUNT(*) AS total_orders,
        DENSE_RANK() OVER (
            PARTITION BY category
            ORDER BY COUNT(*) DESC, item_purchased
        ) AS product_rank
    FROM customer
    GROUP BY category, item_purchased
)
SELECT
    category,
    item_purchased,
    total_orders,
    product_rank
FROM ranked_products
WHERE product_rank <= 3
ORDER BY category, product_rank, item_purchased;
