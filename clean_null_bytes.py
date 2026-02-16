
import os

file_path = 'c:\\Users\\User\\eazzycalculator\\integrated_server.py'

try:
    with open(file_path, 'rb') as f:
        content = f.read()

    # Remove null bytes
    cleaned_content = content.replace(b'\x00', b'')

    # Check if we can decode it as utf-8 now
    text_content = cleaned_content.decode('utf-8', errors='ignore')

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text_content)

    print(f"Successfully cleaned {file_path}")

except Exception as e:
    print(f"Error cleaning file: {e}")
