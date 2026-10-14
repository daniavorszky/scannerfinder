---
title: Listings CSV columns (Outscraper layout)
type: framework
status: stable
updated: 2026-09-30
---

# Outscraper Export Columns

Verified against outscraper.com/google-maps-scraper (data dictionary), 2026-09-16.

## Default columns
name, name_for_emails, subtypes, type, category, phone, website, address, street, county, city, state, state_code, postal_code, country, country_code, latitude, longitude, h3, time_zone, plus_code, area_service, rating, reviews, reviews_link, reviews_tags, reviews_per_score, reviews_per_score_1 to _5, photos_count, photo, street_view, logo, located_in, located_google_id, business_status, working_hours, working_hours_csv_compatible, other_hours, popular_times, typical_time_spent, range, prices, reservation_links, booking_appointment_link, menu_link, order_links, about, description, posts, verified, owner_id, owner_title, owner_link, location_link, location_reviews_link, place_id, google_id, cid, kgmid, reviews_id

## Enrichment add-on columns
domain, email_1 to email_3, Facebook, Instagram, Twitter, Linkedin, Youtube, phone_1 to phone_3, website_title, website_generator, website_description, website_keywords, website_has_fb_pixel, website_has_gtm

## The DataForSEO path writes the same layout
`scripts/fetch_dataforseo.py` maps Business Listings fields onto these column names so Gate 2 runs unchanged: `title` to name, `url` to website, `address_info` to street, city, state, postal_code, `category` to type and category, `additional_categories` to subtypes, `rating` to rating and reviews, `rating_distribution` to reviews_per_score_1 to _5, `place_topics` to reviews_tags as "topic (count)", `attributes` (JSON) to about, `work_time` timetable (JSON) to working_hours, `is_claimed` to verified, `main_image` to photo, `total_photos` to photos_count, `feature_id` to google_id, `check_url` to location_link. Extra columns: domain, email_1 to email_3 (own-domain address first), phone_1 to phone_3, last_updated_time, source (`dataforseo`). Always blank: county, posts, area_service. `business_status` is always `OPERATIONAL` because the database carries no closure flag.

## Used by the pipeline
| Column | Used for |
|---|---|
| name, phone, website, address, street, city, state_code, postal_code, county, latitude, longitude | NAP, slugs, nearby-city math |
| type, subtypes, category | niche match fallback, attribute hints |
| rating, reviews, reviews_per_score_* | ranking within a city, thin flag, schema `AggregateRating` |
| reviews_tags, about, description, posts | enrichment inputs; `description` is the text the Gate 2 thin flag reads |
| working_hours | hours block, schema `openingHoursSpecification` |
| business_status, verified | cleaning, "claimed on Google" hint |
| photo, logo | listing image (hotlinking is not allowed; download or omit) |
| place_id, google_id, cid, location_link | dedupe key, map link |
| area_service | service-area businesses (no street address shown) |

## Found on the pilot (2026-09-29)
- `county` holds neighborhood names ("Southside", "North Naples"), not counties. Use the Census ZIP to county file ([[page-types]] fact sheet, `05-zip-county.json`).
- `website` often carries Google's tracking parameters percent-encoded into the path, which returns a 404. `clean_listings.py` decodes and strips them.
- `reviews_tags` and `posts` can be empty on every row, and `description` nearly so. Then enrichment reads the businesses' own websites ([[enrichment]]).
- The Maps category "Swimming pool contractor" also covers cleaners, repairers, supply stores and unrelated trades.
- `about` is Google's attribute data as JSON (`{"Accessibility": {...}}`) on both sources: every row of a DataForSEO pull, 5,663 of 8,535 rows of the pilot's Outscraper export. It is never prose, so the Gate 2 thin flag reads `description` and treats a JSON `about` as no text ([[listings-cleaning]] rule 7). Enrichment still reads it as data.

## See also
[[listings-cleaning]]
