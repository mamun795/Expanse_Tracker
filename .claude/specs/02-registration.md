# Spec: Registration

## Overview
This step wires up the registration form that already exists in `register.html`
so that new users can create an account. It adds the `POST /register` route,
a `create_user()` DB helper, and sets a Flask session cookie so the user is
immediately logged in after signing up. This is the first step that touches
`flask.session`, so it also installs `SECRET_KEY` on the app.

## Depends on
- Step 01 — Database Setup (users table, `get_db()`, `init_db()`)

## Routes
- `POST /register` — validate form, insert user, set session, redirect to `/profile` — public

The existing `GET /register` route is untouched.

## Database changes
No new tables or columns. Two new helper functions must be added to `database/db.py`:

- `create_user(name, email, password_hash)` — inserts a row into `users`,
  returns the new `id`
- `get_user_by_email(email)` — returns the matching `sqlite3.Row` or `None`

Both must use parameterised queries (`?` placeholders).

## Templates
- **Modify:** `templates/register.html` — already has the form and `{% if error %}` block;
  no structural changes needed. Confirm the form `action` attribute resolves to
  `url_for('register')` and method is `POST`. If the form currently has no `action`,
  add `action="{{ url_for('register') }}"`.

## Files to change
- `app.py` — add `SECRET_KEY`, import `session`/`redirect`/`url_for` from Flask,
  add `POST` to the `register` route's `methods`, implement the POST handler logic
- `database/db.py` — add `create_user()` and `get_user_by_email()`
- `templates/register.html` — add/confirm `action` and `method="post"` on the form

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only
- Parameterised queries only — never use f-strings or `%` in SQL
- Hash passwords with `werkzeug.security.generate_password_hash()` before inserting
- Verify passwords with `werkzeug.security.check_password_hash()` (not used here but import alongside)
- `SECRET_KEY` must be set on `app.config` before any session use; use a hard-coded
  dev string for now (e.g. `"dev-secret-change-in-prod"`) — note it in a comment
- Use `abort(400)` for bad requests, not bare string returns
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values in any new CSS
- Redirect with `redirect(url_for('profile'))` after successful registration
- On duplicate email, re-render `register.html` with `error="An account with that email already exists."`
- On missing fields, re-render `register.html` with `error="All fields are required."`
- Store only `session['user_id'] = new_id` — never store the password or hash in session
- `POST /register` must be in the same route function as `GET /register`, gated by `request.method`

## Definition of done
- [ ] Submitting the form with a new name/email/password creates a row in `users` and
      redirects to `/profile`
- [ ] After registration the profile stub page (or any page) can read `session['user_id']`
      and it equals the new user's database ID
- [ ] Submitting the form a second time with the same email re-renders `register.html`
      with the duplicate-email error message visible
- [ ] Submitting the form with any field blank re-renders `register.html` with the
      missing-fields error message visible
- [ ] The stored `password_hash` is never the plain-text password (verify in DB directly)
- [ ] All existing `pytest` tests still pass
