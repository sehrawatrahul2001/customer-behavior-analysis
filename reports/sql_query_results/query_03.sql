SELECT
    item_purchased,
    ROUND(AVG(CAST(review_rating AS DECIMAL(10, 2))), 2) AS average_product_rating
FROM customer
GROUP BY item_purchased
ORDER BY average_product_rating DESC, item_purchased
LIMIT 5;
