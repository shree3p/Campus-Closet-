# Database Field Mapping
Campus Closet — Final Phase Reference
Prepared by: Jeremiah Trail

This document explains every table in the Campus Closet database, including what each table is used
for, its primary key, and any foreign keys it holds.

---

## 1. User
**What it does:** Stores every account on the platform — both students and admins.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String(120) | Full name of the user |
| username | String(80) | Unique username |
| email | String(255) | Unique SCSU email |
| password_hash | String(255) | Hashed password |
| role | String(20) | Either "student" or "admin" |
| account_status | String(20) | Either "active" or suspended |
| created_at | DateTime | When the account was created |

**Primary key:** id
**Foreign keys:** None

---

## 2. Profile
**What it does:** Stores optional profile details for each user, like their major and bio.
One profile per user.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key → User.id |
| major | String(120) | Student's major |
| bio | Text | Short personal description |
| profile_image | String(255) | URL to profile photo |
| contact_preferences | String(255) | Default: "In-app messages" |

**Primary key:** id
**Foreign keys:** user_id → User.id (unique, one-to-one)

---

## 3. Category
**What it does:** Stores the item categories that listings are organized under.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| name | String(80) | Unique category name |
| description | String(255) | Short description of the category |

**Primary key:** id
**Foreign keys:** None

**Seeded categories:** Clothing, Dorm Furniture, School Supplies, Electronics, Other

---

## 4. Listing
**What it does:** Stores every item posted for exchange or pickup on the platform.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key → User.id (the seller/owner) |
| category_id | Integer | Foreign key → Category.id |
| title | String(150) | Item title |
| description | Text | Full item description |
| item_condition | String(80) | e.g. "Good", "Very Good", "Like New" |
| pickup_location | String(120) | Where to pick up the item on campus |
| availability_status | String(40) | Default: "Available" |
| image_url | String(255) | Optional image link |
| created_at | DateTime | When the listing was posted |

**Primary key:** id
**Foreign keys:** user_id → User.id, category_id → Category.id

---

## 5. Favorite
**What it does:** Tracks which listings a user has saved/favorited. Each row represents
one user saving one listing.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key → User.id |
| listing_id | Integer | Foreign key → Listing.id |
| saved_at | DateTime | When the item was favorited |

**Primary key:** id
**Foreign keys:** user_id → User.id, listing_id → Listing.id
**Unique constraint:** A user can only favorite the same listing once (uq_favorite_user_listing)

---

## 6. Conversation
**What it does:** Represents a messaging thread between two users about a specific listing.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| listing_id | Integer | Foreign key → Listing.id |
| participant_one_id | Integer | Foreign key → User.id |
| participant_two_id | Integer | Foreign key → User.id |
| created_at | DateTime | When the conversation started |
| last_updated | DateTime | When the last message was sent |

**Primary key:** id
**Foreign keys:** listing_id → Listing.id, participant_one_id → User.id, participant_two_id → User.id

---

## 7. Message
**What it does:** Stores individual messages sent within a conversation.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| conversation_id | Integer | Foreign key → Conversation.id |
| sender_id | Integer | Foreign key → User.id |
| message_text | Text | The actual message content |
| is_read | Boolean | Whether the recipient has read it |
| created_at | DateTime | When the message was sent |

**Primary key:** id
**Foreign keys:** conversation_id → Conversation.id, sender_id → User.id

---

## 8. Report
**What it does:** Stores reports submitted by users about a listing or another user.
An admin reviews and resolves the report.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| reporter_id | Integer | Foreign key → User.id (who filed the report) |
| listing_id | Integer | Foreign key → Listing.id (optional) |
| reported_user_id | Integer | Foreign key → User.id (optional) |
| reason | String(120) | Short reason for the report |
| description | Text | Full explanation |
| status | String(40) | Default: "Pending" |
| reviewed_by_admin_id | Integer | Foreign key → User.id (admin who reviewed it) |
| created_at | DateTime | When the report was filed |
| resolved_at | DateTime | When the report was resolved (optional) |

**Primary key:** id
**Foreign keys:** reporter_id → User.id, listing_id → Listing.id, reported_user_id → User.id,
reviewed_by_admin_id → User.id

---

## 9. Review
**What it does:** Stores ratings and comments left by one user about another user,
usually after a completed exchange.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| reviewer_id | Integer | Foreign key → User.id (who wrote the review) |
| reviewee_id | Integer | Foreign key → User.id (who received the review) |
| listing_id | Integer | Foreign key → Listing.id (optional, for context) |
| rating | Integer | Numeric rating |
| comment | Text | Written feedback |
| created_at | DateTime | When the review was posted |

**Primary key:** id
**Foreign keys:** reviewer_id → User.id, reviewee_id → User.id, listing_id → Listing.id

---

## 10. Notification
**What it does:** Stores in-app alerts sent to a user, such as new messages or
listing status updates.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key → User.id |
| notification_type | String(60) | Category of notification |
| message | String(255) | The notification text |
| is_read | Boolean | Whether the user has seen it |
| created_at | DateTime | When the notification was created |

**Primary key:** id
**Foreign keys:** user_id → User.id

---

## 11. ActivityLog
**What it does:** Records actions taken by users for tracking and admin review purposes,
such as creating a listing or logging in.

| Field | Type | Notes |
|---|---|---|
| id | Integer | Primary key |
| user_id | Integer | Foreign key → User.id |
| action_type | String(80) | Short label for the action (e.g. "create_listing") |
| description | String(255) | More detail about what happened |
| created_at | DateTime | When the action occurred |

**Primary key:** id
**Foreign keys:** user_id → User.id
