-- Customer Behavior & Revenue Insights Analysis
-- Cleaned source table: customer
-- Engineered fields available:
--   age_group, purchase_frequency_days, customer_lifetime_segment

-- 1. Revenue contribution by gender
SELECT
    gender,
    ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
GROUP BY gender
ORDER BY total_revenue DESC;

-- 2. Discounted customers spending above the overall average
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

-- 3. Top five products by average review rating
SELECT
    item_purchased,
    ROUND(AVG(CAST(review_rating AS DECIMAL(10, 2))), 2) AS average_product_rating
FROM customer
GROUP BY item_purchased
ORDER BY average_product_rating DESC, item_purchased
LIMIT 5;

-- 4. Average purchase amount for standard vs express shipping
SELECT
    shipping_type,
    ROUND(AVG(purchase_amount), 2) AS average_purchase_amount
FROM customer
WHERE shipping_type IN ('Standard', 'Express')
GROUP BY shipping_type
ORDER BY average_purchase_amount DESC;

-- 5. Subscriber vs non-subscriber spend
SELECT
    subscription_status,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(purchase_amount), 2) AS average_spend,
    ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
GROUP BY subscription_status
ORDER BY total_revenue DESC, average_spend DESC;

-- 6. Products with the highest share of discounted purchases
SELECT
    item_purchased,
    ROUND(100.0 * AVG(CASE WHEN discount_applied = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS discount_rate_pct
FROM customer
GROUP BY item_purchased
ORDER BY discount_rate_pct DESC, item_purchased
LIMIT 5;

-- 7. Customer segmentation by previous purchases
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

-- 8. Top three products within each category
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

-- 9. Subscription mix among repeat buyers
WITH repeat_buyers AS (
    SELECT *
    FROM customer
    WHERE previous_purchases > 5
)
SELECT
    subscription_status,
    COUNT(*) AS repeat_buyers,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS repeat_buyer_share_pct
FROM repeat_buyers
GROUP BY subscription_status
ORDER BY repeat_buyers DESC;

-- 10. Revenue contribution by age group
SELECT
    age_group,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(100.0 * SUM(purchase_amount) / SUM(SUM(purchase_amount)) OVER (), 2) AS revenue_contribution_pct
FROM customer
GROUP BY age_group
ORDER BY total_revenue DESC;

-- 11. Payment method revenue performance
SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(AVG(purchase_amount), 2) AS average_order_value
FROM customer
GROUP BY payment_method
ORDER BY total_revenue DESC, average_order_value DESC;

-- 12. Locations combining stronger revenue and subscriber share
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

-- 13. Customer lifetime segment performance by shipping type
SELECT
    customer_lifetime_segment,
    shipping_type,
    COUNT(*) AS total_customers,
    ROUND(AVG(purchase_amount), 2) AS average_spend,
    ROUND(AVG(CAST(review_rating AS DECIMAL(10, 2))), 2) AS average_rating
FROM customer
GROUP BY customer_lifetime_segment, shipping_type
ORDER BY customer_lifetime_segment, average_spend DESC, total_customers DESC;
