# SQL Validation Report

These outputs were generated from the validated local SQLite database created from the cleaned `customer` table.

## Query 1. Revenue by Gender

```sql
SELECT
    gender,
    ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
GROUP BY gender
ORDER BY total_revenue DESC;
```

CSV output: `reports/sql_query_results/query_01.csv`  
SQL file: `reports/sql_query_results/query_01.sql`

| gender | total_revenue |
| --- | --- |
| Male | 157890.0 |
| Female | 75191.0 |

## Query 2. Discounted Customers Spending Above Average

```sql
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
```

CSV output: `reports/sql_query_results/query_02.csv`  
SQL file: `reports/sql_query_results/query_02.sql`

| customer_id | purchase_amount |
| --- | --- |
| 43 | 100 |
| 96 | 100 |
| 194 | 100 |
| 205 | 100 |
| 244 | 100 |
| 249 | 100 |
| 456 | 100 |
| 519 | 100 |
| 582 | 100 |
| 616 | 100 |
| 770 | 100 |
| 862 | 100 |

## Query 3. Top Rated Products

```sql
SELECT
    item_purchased,
    ROUND(AVG(CAST(review_rating AS DECIMAL(10, 2))), 2) AS average_product_rating
FROM customer
GROUP BY item_purchased
ORDER BY average_product_rating DESC, item_purchased
LIMIT 5;
```

CSV output: `reports/sql_query_results/query_03.csv`  
SQL file: `reports/sql_query_results/query_03.sql`

| item_purchased | average_product_rating |
| --- | --- |
| Gloves | 3.86 |
| Sandals | 3.84 |
| Boots | 3.82 |
| Hat | 3.8 |
| Handbag | 3.78 |

## Query 4. Average Purchase Amount by Shipping Type

```sql
SELECT
    shipping_type,
    ROUND(AVG(purchase_amount), 2) AS average_purchase_amount
FROM customer
WHERE shipping_type IN ('Standard', 'Express')
GROUP BY shipping_type
ORDER BY average_purchase_amount DESC;
```

CSV output: `reports/sql_query_results/query_04.csv`  
SQL file: `reports/sql_query_results/query_04.sql`

| shipping_type | average_purchase_amount |
| --- | --- |
| Express | 60.48 |
| Standard | 58.46 |

## Query 5. Subscriber vs Non-Subscriber Spend

```sql
SELECT
    subscription_status,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(purchase_amount), 2) AS average_spend,
    ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
GROUP BY subscription_status
ORDER BY total_revenue DESC, average_spend DESC;
```

CSV output: `reports/sql_query_results/query_05.csv`  
SQL file: `reports/sql_query_results/query_05.sql`

| subscription_status | total_customers | average_spend | total_revenue |
| --- | --- | --- | --- |
| No | 2847 | 59.87 | 170436.0 |
| Yes | 1053 | 59.49 | 62645.0 |

## Query 6. Products with Highest Discount Usage

```sql
SELECT
    item_purchased,
    ROUND(100.0 * AVG(CASE WHEN discount_applied = 'Yes' THEN 1.0 ELSE 0.0 END), 2) AS discount_rate_pct
FROM customer
GROUP BY item_purchased
ORDER BY discount_rate_pct DESC, item_purchased
LIMIT 5;
```

CSV output: `reports/sql_query_results/query_06.csv`  
SQL file: `reports/sql_query_results/query_06.sql`

| item_purchased | discount_rate_pct |
| --- | --- |
| Hat | 50.0 |
| Sneakers | 49.66 |
| Coat | 49.07 |
| Sweater | 48.17 |
| Pants | 47.37 |

## Query 7. Customer Segmentation by Previous Purchases

```sql
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
```

CSV output: `reports/sql_query_results/query_07.csv`  
SQL file: `reports/sql_query_results/query_07.sql`

| customer_segment | number_of_customers |
| --- | --- |
| New | 83 |
| Returning | 701 |
| Loyal | 3116 |

## Query 8. Top Products Within Each Category

```sql
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
```

CSV output: `reports/sql_query_results/query_08.csv`  
SQL file: `reports/sql_query_results/query_08.sql`

| category | item_purchased | total_orders | product_rank |
| --- | --- | --- | --- |
| Accessories | Jewelry | 171 | 1 |
| Accessories | Belt | 161 | 2 |
| Accessories | Sunglasses | 161 | 3 |
| Clothing | Blouse | 171 | 1 |
| Clothing | Pants | 171 | 2 |
| Clothing | Shirt | 169 | 3 |
| Footwear | Sandals | 160 | 1 |
| Footwear | Shoes | 150 | 2 |
| Footwear | Sneakers | 145 | 3 |
| Outerwear | Jacket | 163 | 1 |
| Outerwear | Coat | 161 | 2 |

## Query 9. Subscription Mix Among Repeat Buyers

```sql
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
```

CSV output: `reports/sql_query_results/query_09.csv`  
SQL file: `reports/sql_query_results/query_09.sql`

| subscription_status | repeat_buyers | repeat_buyer_share_pct |
| --- | --- | --- |
| No | 2518 | 72.44 |
| Yes | 958 | 27.56 |

## Query 10. Revenue Contribution by Age Group

```sql
SELECT
    age_group,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(100.0 * SUM(purchase_amount) / SUM(SUM(purchase_amount)) OVER (), 2) AS revenue_contribution_pct
FROM customer
GROUP BY age_group
ORDER BY total_revenue DESC;
```

CSV output: `reports/sql_query_results/query_10.csv`  
SQL file: `reports/sql_query_results/query_10.sql`

| age_group | total_revenue | revenue_contribution_pct |
| --- | --- | --- |
| Young Adult | 62143.0 | 26.66 |
| Middle-aged | 59197.0 | 25.4 |
| Adult | 55978.0 | 24.02 |
| Senior | 55763.0 | 23.92 |

## Query 11. Payment Method Revenue Performance

```sql
SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(SUM(purchase_amount), 2) AS total_revenue,
    ROUND(AVG(purchase_amount), 2) AS average_order_value
FROM customer
GROUP BY payment_method
ORDER BY total_revenue DESC, average_order_value DESC;
```

CSV output: `reports/sql_query_results/query_11.csv`  
SQL file: `reports/sql_query_results/query_11.sql`

| payment_method | total_orders | total_revenue | average_order_value |
| --- | --- | --- | --- |
| Credit Card | 671 | 40310.0 | 60.07 |
| PayPal | 677 | 40109.0 | 59.25 |
| Cash | 670 | 40002.0 | 59.7 |
| Debit Card | 636 | 38742.0 | 60.92 |
| Venmo | 634 | 37374.0 | 58.95 |
| Bank Transfer | 612 | 36544.0 | 59.71 |

## Query 12. Top Revenue Locations with Subscription Share

```sql
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
```

CSV output: `reports/sql_query_results/query_12.csv`  
SQL file: `reports/sql_query_results/query_12.sql`

| location | total_customers | total_revenue | average_purchase_amount | subscriber_share_pct |
| --- | --- | --- | --- | --- |
| Montana | 96 | 5784.0 | 60.25 | 26.04 |
| Illinois | 92 | 5617.0 | 61.05 | 23.91 |
| California | 95 | 5605.0 | 59.0 | 30.53 |
| Idaho | 93 | 5587.0 | 60.08 | 20.43 |
| Nevada | 87 | 5514.0 | 63.38 | 34.48 |
| Alabama | 89 | 5261.0 | 59.11 | 24.72 |
| New York | 87 | 5257.0 | 60.43 | 24.14 |
| North Dakota | 83 | 5220.0 | 62.89 | 28.92 |
| West Virginia | 81 | 5174.0 | 63.88 | 34.57 |
| Nebraska | 87 | 5172.0 | 59.45 | 28.74 |

## Query 13. Customer Lifetime Segments by Shipping Behavior

```sql
SELECT
    customer_lifetime_segment,
    shipping_type,
    COUNT(*) AS total_customers,
    ROUND(AVG(purchase_amount), 2) AS average_spend,
    ROUND(AVG(CAST(review_rating AS DECIMAL(10, 2))), 2) AS average_rating
FROM customer
GROUP BY customer_lifetime_segment, shipping_type
ORDER BY customer_lifetime_segment, average_spend DESC, total_customers DESC;
```

CSV output: `reports/sql_query_results/query_13.csv`  
SQL file: `reports/sql_query_results/query_13.sql`

| customer_lifetime_segment | shipping_type | total_customers | average_spend | average_rating |
| --- | --- | --- | --- | --- |
| Growth Customer | Free Shipping | 60 | 52.82 | 3.85 |
| Growth Customer | Express | 46 | 52.61 | 3.8 |
| Growth Customer | Next Day Air | 57 | 51.33 | 3.85 |
| Growth Customer | Store Pickup | 46 | 49.02 | 3.58 |
| Growth Customer | 2-Day Shipping | 40 | 47.75 | 3.7 |
| Growth Customer | Standard | 44 | 45.82 | 3.98 |
| High-Value Customer | 2-Day Shipping | 459 | 64.63 | 3.77 |
| High-Value Customer | Express | 462 | 64.38 | 3.78 |
| High-Value Customer | Store Pickup | 461 | 64.25 | 3.7 |
| High-Value Customer | Free Shipping | 479 | 63.73 | 3.73 |
| High-Value Customer | Next Day Air | 454 | 62.53 | 3.7 |
| High-Value Customer | Standard | 466 | 62.29 | 3.81 |
