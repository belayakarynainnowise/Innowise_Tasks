-- Task 1

/*
Вывести количество фильмов в каждой категории,
отсортировать по убыванию.
 */

SELECT  c.name, COUNT(f_c.film_id) AS film_count 
FROM category AS c
INNER JOIN film_category as f_c ON c.category_id=f_c.category_id
GROUP BY c.name
ORDER BY film_count DESC;

-- Task 2

/*
Вывести 10 актеров, чьи фильмы большего всего арендовали,
отсортировать по убыванию.
 */
 
WITH film_rental AS 
                  (SELECT f.film_id,f.title,COUNT(f.film_id) AS film_count_in_rental
                   FROM rental AS r
                   INNER JOIN inventory AS i ON i.inventory_id =r.inventory_id
                   INNER JOIN film AS f ON i.film_id=f.film_id
                   GROUP BY f.film_id)
SELECT a.actor_id,a.first_name,a.last_name, SUM(film_count_in_rental) AS rental_count
FROM actor AS a
INNER JOIN film_actor AS f_a ON a.actor_id=f_a.actor_id
INNER JOIN film_rental AS f_r ON f_r.film_id=f_a.film_id
GROUP BY a.actor_id
ORDER BY rental_count DESC
LIMIT 10;


-- Task 3

/*
Вывести категорию фильмов,
на которую потратили больше всего денег
*/

SELECT c.name, SUM(p.amount) AS payment_sum
FROM payment AS p 
INNER JOIN rental AS r ON p.rental_id=r.rental_id
INNER JOIN inventory AS i on r.inventory_id=i.inventory_id
INNER JOIN film AS f on i.film_id=f.film_id
INNER JOIN film_category AS f_c ON f.film_id=f_c.film_id
INNER JOIN category AS c ON f_c.category_id=c.category_id
GROUP BY c.name
ORDER BY payment_sum DESC
LIMIT 1;


-- Task 4

/*
Вывести названия фильмов, которых нет в inventory.
Написать запрос без использования оператора IN.
*/

SELECT f.title
FROM film AS f 
LEFT JOIN inventory AS i ON f.film_id=i.film_id
WHERE i.film_id IS NULL;


-- Task 5

/*
Вывести топ 3 актеров, которые больше всего появлялись в фильмах в категории “Children”.
Если у нескольких актеров одинаковое кол-во фильмов, вывести всех.
*/

SELECT a.actor_id,a.last_name,a.first_name,COUNT(f.film_id) AS amount
FROM film AS f
INNER JOIN film_category AS f_c ON f.film_id=f_c.film_id
INNER JOIN category AS c ON c.category_id=f_c.category_id
INNER JOIN film_actor AS f_a ON f_a.film_id=f.film_id
INNER JOIN actor AS a ON f_a.actor_id=a.actor_id
WHERE c.name='Children'
GROUP BY a.actor_id
ORDER BY amount DESC
FETCH FIRST 3 ROWS WITH TIES;


-- Task 6

/*
Вывести города с количеством активных и неактивных клиентов
(активный — customer.active = 1). 
Отсортировать по количеству неактивных клиентов по убыванию
*/

SELECT c.city,
COUNT(CASE WHEN cust.active=1 THEN 1 ELSE NULL END) AS active_count,
COUNT(CASE WHEN cust.active=0 THEN 1 ELSE NULL END) as inactive_count
FROM city AS c
INNER JOIN address AS a ON a.city_id=c.city_id
INNER JOIN customer AS cust ON cust.address_id=a.address_id
GROUP BY c.city_id
ORDER BY inactive_count DESC;


-- Task 7

/*
Вывести категорию фильмов, у которой самое большое кол-во часов суммарной аренды в городах
(customer.address_id в этом city),
и которые начинаются на букву “a”.
То же самое сделать для городов в которых есть символ “-”. Написать все в одном запросе.
*/

WITH category_ren_count AS
                         (SELECT cat.name, SUM(age(r.return_date,r.rental_date)) AS rental_time, c.city
                          FROM category AS cat
                          INNER JOIN film_category AS f_cat ON f_cat.category_id=cat.category_id
                          INNER JOIN film AS f ON f_cat.film_id=f.film_id
                          INNER JOIN inventory AS i ON i.film_id=f.film_id
                          INNER JOIN rental AS r ON r.inventory_id=i.inventory_id
                          INNER JOIN customer AS cus ON r.customer_id=cus.customer_id
                          INNER JOIN address AS a ON cus.address_id=a.address_id
                          INNER JOIN city AS c ON c.city_id=a.city_id
                          GROUP BY cat.name,c.city)
SELECT DISTINCT ON(city) name, rental_time,city
FROM category_ren_count
WHERE rental_time IN 
             (SELECT MAX(rental_time)
              FROM category_ren_count
              GROUP BY city)
		   AND 
             (city LIKE'%-%'
			  OR
              LOWER(city) LIKE 'a%')
ORDER BY city, name;