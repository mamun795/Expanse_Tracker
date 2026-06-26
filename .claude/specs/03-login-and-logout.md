# Spec: Login and Logout

## Overview
This step wires up the login form that already exists in `login.html` so that
registered users can authenticate, and replaces the `/logout` stub so users can
end their session. It adds a `POST /login` route that validates credentials with
`check_password_hash`, writes `session['user_id']` on success, and a `GET /logout`
route that clears the session and redirects to the landing page. Together these
two routes complete the authentication round-trip started by Step 02.

## Depends on
- Step 01 — Database Setup (`get_db()`, `users` table)
- Step 02 — Registration (`get_user_by_email()`, `session['user_id']` convention)

## Routes
- `POST /login` — validate email + password, set session, redirect to `/profile` — public
- `GET /logout` — clear session, redirect to `/` — logged-in (no hard guard required yet)

The existing `GET /login` route is untouched except the route decorator gains `"POST"`
in its `methods` list.

## Database changes
No new tables or columns.

One new helper function must be added to `database/db.py`:

- `get_user_by_id(user_id)` — returns the matching `sqlite3.Row` or `None`;
  needed by downstream steps (profile, expenses) and good to introduce here
  alongside the login flow.

`get_user_by_email()` already exists from Step 02 and is reused as-is.

## Templates
- **Modify:** `templates/login.html` — confirm the form has
  `action="{{ url_for('login') }}"` and `method="post"`. Add both if absent.
  Ensure there is a `{% if error %}<p class="error">{{ error }}</p>{% endif %}`
  block visible above or inside the form.

## Files to change
- `app.py` — add `"POST"` to the `login` route's `methods`, implement the POST
  handler; replace the `logout` stub with a real route that clears the session
  and redirects
- `database/db.py` — add `get_user_by_id(user_id)`
- `templates/login.html` — add/confirm `action`, `method="post"`, and error block

## Files to create
None.

## New dependencies
No new dependencies. `check_password_hash` is already imported from
`werkzeug.security` in `app.py`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only
- Parameterised queries only — never use f-strings or `%` in SQL
- Verify passwords with `werkzeug.security.check_password_hash(row['password_hash'], password)`
- Never store the password or hash in the session — only `session['user_id']`
- On login success: `session['user_id'] = row['id']`, then
  `redirect(url_for('profile'))`
- On wrong email or wrong password: re-render `login.html` with
  `error="Invalid email or password."` — use the same message for both cases
  to avoid user enumeration
- On missing fields: re-render `login.html` with `error="All fields are required."`
- `POST /login` must be in the same route function as `GET /login`, gated by
  `request.method`
- `GET /logout` must call `session.clear()`, then `redirect(url_for('landing'))`
- Use `abort()` for genuine HTTP errors — not bare string returns
- All templates extend `base.html`
- Use CSS variables — never hardcode hex values in any new CSS

## Definition of done
- [ ] Submitting the login form with the demo credentials (`demo@spendly.com` /
      `demo123`) sets `session['user_id']` and redirects to `/profile`
- [ ] After login, `session['user_id']` equals the demo user's database ID
- [ ] Submitting with a correct email but wrong password re-renders `login.html`
      with `"Invalid email or password."` visible — no redirect
- [ ] Submitting with an email that does not exist re-renders `login.html` with
      `"Invalid email or password."` visible — no redirect
- [ ] Submitting with any field blank re-renders `login.html` with
      `"All fields are required."` visible
- [ ] Visiting `/logout` clears `session['user_id']` and redirects to `/`
- [ ] Visiting `/logout` when not logged in also redirects to `/` without error
- [ ] `get_user_by_id()` returns the correct row when given a valid ID and
      `None` when given an unknown ID
- [ ] All existing `pytest` tests still pass
