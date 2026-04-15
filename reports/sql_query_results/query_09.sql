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
