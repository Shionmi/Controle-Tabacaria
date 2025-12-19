import sys

# Read file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace problematic Unicode characters
replacements = {
    '\u2550': '=',  # Box drawing
    '\u2554': '+',  # Box drawing
    '\u2557': '+',  # Box drawing
    '\u2560': '+',  # Box drawing
    '\u2563': '+',  # Box drawing
    '\u255a': '+',  # Box drawing
    '\u255d': '+',  # Box drawing
    '\u2551': '|',  # Box drawing
    '\ud83c\udf0d': '',  # Globe emoji
    '\u26a0\ufe0f': '',  # Warning emoji
    '\ud83d\udca1': '',  # Light bulb emoji
    '\ud83c\udfe0': '',  # House emoji
    '\ud83d\udcbb': '',  # Computer emoji
    '\ud83d\udcf1': '',  # Phone emoji
    '\u2705': '',  # Checkmark emoji
    '\ud83c\udfea': '',  # Store emoji
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Write back
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Unicode characters replaced successfully")
