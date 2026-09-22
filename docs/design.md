# Spend Tracker — UI/UX Design

## Design Direction

Create a clean, modern, lightweight SaaS-style interface.

The application should prioritize:
- clarity
- speed
- accessibility
- responsive behavior
- obvious expense-entry workflow

Use a light theme by default.

Avoid:
- excessive gradients
- excessive animations
- decorative elements that reduce readability
- complex navigation
- unnecessary dashboards/charts

## Main Layout

```text
------------------------------------------------
 Spend Tracker                         [Profile]
------------------------------------------------

 [ Total Spend ] [ MoM Change ] [ Categories ]

------------------------------------------------
 Add Expense
------------------------------------------------

 Amount       Category
 [_______]    [___________]

 Note
 [____________________________]

 Date         [___________]

              [ Add Expense ]

------------------------------------------------
 Spending by Category
------------------------------------------------

 Food              ₹4,500
 Transport         ₹2,100
 Shopping          ₹3,200

------------------------------------------------
 Recent Expenses
------------------------------------------------

 Date       Category       Note       Amount
 ------------------------------------------------
 Sep 22     Food           Lunch      ₹450
 Sep 21     Transport      Uber       ₹320
```

## Components

### Summary Cards
Display:
- Current month total spend.
- Month-over-month percentage change.
- Number of expenses or another useful non-conflicting metric if desired.

Cards should be compact and readable.

### Add Expense Form
Fields:
- Amount
- Category
- Note
- Date

Requirements:
- clear labels
- visible validation errors
- disabled/loading submit state
- success feedback
- keyboard-friendly controls

### Category Breakdown
Use simple cards, progress bars, or a lightweight chart.

Do not add a chart library unless necessary.

### Expense List
Display:
- date
- category
- note
- amount

Include:
- empty state
- loading state
- error state

If filters are exposed in the UI:
- category
- start date
- end date

## Responsive Design

Desktop:
- centered content with comfortable max width.
- summary cards in a row.
- form and summary sections use available horizontal space.

Tablet:
- cards wrap naturally.
- maintain readable spacing.

Mobile:
- single-column layout.
- full-width form controls.
- horizontally scrollable table only if necessary; prefer stacked expense cards when practical.
- touch targets should be comfortable.

## Accessibility

- Semantic HTML.
- Labels associated with inputs.
- Keyboard navigation.
- Visible focus states.
- Sufficient text/background contrast.
- Do not rely on color alone for error/success states.
- Use accessible button text.

## UX States

Every API-driven section should support:
1. Loading
2. Success
3. Empty
4. Validation error
5. Server/API error

Avoid blocking the entire page for a single API failure.

## Visual Style

Suggested:
- neutral background
- white cards
- subtle borders/shadows
- restrained accent color
- clear typography hierarchy
- consistent spacing
- small radius, not excessive rounded elements

The UI is intentionally secondary to backend correctness.
