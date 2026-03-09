# Semantic Token Categories Reference

> Source: `migration/semantic-token-categories.png`
>
> This table defines which semantic token categories map to which elements and components.

| Category | Subtypes / Tokens | Elements to Target | Used In Components | Notes |
|----------|-------------------|--------------------|--------------------|-------|
| **interactive** | primary, secondary, tertiary | Fill, Text, Icon | Button, Circle Button | Used for all major action elements |
| **disabled** | text (muted), background (greyed) | Fill, Text, Icon | Button, Circle Button, Checkbox, Radio Button | Used to indicate non-interactive elements |
| **focus** | focus border color | Border | Button, Input Field, Text area, Radio Button | Tokenised outline ring |
| **text** | primary, secondary, placeholder, inverse, on-accent | Text | Button, Country Picker, Date of Birth | Semantic text use cases |
| **icon** | primary, secondary | Icon | Button | Applied to icon instances |
| **border** | default, on-accent, inverse | Border | Button, Accordion | For dividing or framing elements |
| **input** | border, fill, text | Fill, Text, Icon | Text Input, Text area, Double Range Input | Includes hover and active states |
| **feedback** | error, success, warning, info (fill, border, text) | Fill, Text, Icon | Alert | Multichannel: Visual + (future) voice/sound |
| **active / selected** | fill, border, text | Fill, Text, Icon | RadioButton, Checkbox, Chip (future) | For selected/toggled states |
| **status** | draft, active, positive, critical, attention, neutral, etc | Fill, Text, Icon | Badge (presale, critical, VIP, etc.) | Metadata indicators |
| **elevation** | level-0, level-1 to level-4 (overlay) | Box-shadow | Card, Modal, Tooltip | Maps to shadow & background fills |
