# ER Relationships
Campus Closet — Final Phase Reference
Prepared by: Jeremiah Trail

This document explains how the database tables connect to each other in plain language.

---

## User → Profile
**One-to-one relationship.**
Every user has exactly one profile. The Profile table holds the extra details (major, bio, photo)
that don't need to be on the main User table. If a user is deleted, their profile is deleted too.

---

## User → Listing
**One-to-many relationship.**
One user can create many listings. Each listing has a user_id that points back to the user who
posted it. That user is referred to as the "owner" of the listing.

---

## Category → Listing
**One-to-many relationship.**
One category (like "Clothing" or "Electronics") can have many listings under it. Each listing
must belong to exactly one category via category_id.

---

## User → Favorite → Listing
**Many-to-many relationship through Favorite.**
A user can favorite many listings. A listing can be favorited by many users. The Favorite table
sits in the middle and connects them. Each row in Favorite is one user saving one listing.
A user cannot favorite the same listing twice.

---

## Conversation → Message
**One-to-many relationship.**
One conversation holds many messages. A conversation is a thread between two users about a
specific listing. Every individual message belongs to one conversation via conversation_id.

---

## User → Conversation (two participants)
**Each conversation has exactly two users.**
participant_one_id and participant_two_id both point to User.id. This means every conversation
always involves exactly two people — typically the listing owner and an interested buyer.

---

## Listing → Conversation
**One-to-many relationship.**
One listing can have multiple conversations about it (from different interested users).
Each conversation is tied to the listing it started from via listing_id.

---

## User → Message (as sender)
**One-to-many relationship.**
One user can send many messages. Each message has a sender_id pointing to the user who wrote it.

---

## User → Report (as reporter)
**One-to-many relationship.**
A user can file many reports. Each report stores the reporter_id of who submitted it.

---

## User → Report (as reviewed_by_admin)
**One-to-many relationship.**
An admin user can review many reports. The reviewed_by_admin_id field on the Report table
points to the admin's User.id. This field is optional — it stays empty until an admin acts on it.

---

## Listing → Report
**One-to-many relationship.**
A listing can be reported multiple times by different users. The listing_id on Report is optional
because a report might be about a user rather than a specific listing.

---

## User → Report (as reported_user)
**One-to-many relationship.**
A user can be reported by other users. The reported_user_id on Report points to the user being
reported. This field is optional — a report might target a listing instead of a user directly.

---

## User → Review (as reviewer and reviewee)
**One user can write many reviews. One user can receive many reviews.**
The Review table uses two separate foreign keys to handle this:
- reviewer_id → the user who wrote the review
- reviewee_id → the user who received the review
This means one user can be both a reviewer and a reviewee in different review records.

---

## Listing → Review
**One-to-many relationship.**
A listing can have multiple reviews associated with it. The listing_id on Review is optional —
it provides context for which item the exchange was about.

---

## User → Notification
**One-to-many relationship.**
One user can receive many notifications. Each notification belongs to one user via user_id.
Notifications are deleted when the user is deleted.

---

## User → ActivityLog
**One-to-many relationship.**
One user can have many activity log entries. Each log entry records one action that user took,
such as creating a listing or logging in. Logs are deleted when the user is deleted.

---

## Summary Table

| Relationship | Type | How it connects |
|---|---|---|
| User → Profile | One-to-one | Profile.user_id → User.id |
| User → Listing | One-to-many | Listing.user_id → User.id |
| Category → Listing | One-to-many | Listing.category_id → Category.id |
| User ↔ Listing (Favorites) | Many-to-many | Through Favorite table |
| Conversation → Message | One-to-many | Message.conversation_id → Conversation.id |
| User → Conversation | Two foreign keys | participant_one_id, participant_two_id → User.id |
| Listing → Conversation | One-to-many | Conversation.listing_id → Listing.id |
| User → Message | One-to-many | Message.sender_id → User.id |
| User → Report (reporter) | One-to-many | Report.reporter_id → User.id |
| User → Report (admin) | One-to-many | Report.reviewed_by_admin_id → User.id |
| Listing → Report | One-to-many | Report.listing_id → Listing.id |
| User → Report (reported) | One-to-many | Report.reported_user_id → User.id |
| User → Review (writer) | One-to-many | Review.reviewer_id → User.id |
| User → Review (receiver) | One-to-many | Review.reviewee_id → User.id |
| Listing → Review | One-to-many | Review.listing_id → Listing.id |
| User → Notification | One-to-many | Notification.user_id → User.id |
| User → ActivityLog | One-to-many | ActivityLog.user_id → User.id |
