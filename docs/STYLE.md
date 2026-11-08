# Screen style — Finance Shield

Date: 8 November 2026.

The screen is a card risk desk. It is the tool a banker uses to read one score. It is not a marketing dashboard.

## Look

- Sidebar is navy (`#0b1f33`). The mark is **FINANCE SHIELD** and the line under it is **Card risk desk**.
- The page background is a cool grey. Each page opens with a white title block and a navy bar on the left.
- Number tiles are white, square, and quiet. They do not use a bright gradient.
- **Allow** is green. **Review** is amber. Amber means “a person should look.” It does not mean the card was declined.
- The decision sheet is a plain table. Case, disposition, fraud score, amount, and the short note come first. The anonymous V columns stay inside **Model inputs**.

## Words

- Say what happened in one or two sentences before any feature name.
- A score under 95% is: this looks normal, and no message goes to the customer.
- A score of 95% or more is: this looks suspicious, the case comes to the banker, and the customer would get a phone alert and an email at that moment.
- The customer message says the card has not been blocked.
- Label that message **Preview only**. This screen does not send a real alert or a real email.

## What the screen does not show

- A live count of today’s payments.
- Money saved.
- A latency such as 41 ms.
- Accuracy as the headline.
- A picture that pretends the model saw a merchant, a city, or a cardholder.

Those figures are not in this repository. Leaving them off is part of the style.
