#!/usr/bin/env python3
"""
rebuild_ui.py — Complete UI replacement for Geodetic Knife.
Mobile-first PWA with modern engineering aesthetic.
Dark mode default, bottom nav, card-based layout, Inter + JetBrains Mono.
"""
import os, sys, shutil

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, 'public', 'index.html')
    
    # Find the new index.html (look for the downloaded version)
    new_html = os.path.join(script_dir, 'new_index.html')
    
    if not os.path.isfile(new_html):
        print('[ERR] new_index.html not found.')
        print('Place the new index.html in the project root as "new_index.html" and run again.')
        sys.exit(1)
    
    # Backup current
    if os.path.isfile(html_path):
        backup = html_path + '.bak.' + os.path.basename(script_dir)
        shutil.copy2(html_path, backup)
        print('[OK] Backed up current HTML to: ' + os.path.basename(backup))
    
    # Replace
    shutil.copy2(new_html, html_path)
    print('[OK] Replaced public/index.html with new UI')
    
    # Cleanup
    os.remove(new_html)
    print('[OK] Cleaned up new_index.html')
    
    print()
    print('=' * 50)
    print('  UI rebuilt successfully!')
    print('  - Mobile-first PWA design')
    print('  - Dark/Light theme')
    print('  - Bottom tab navigation')
    print('  - Card-based layout')
    print('  - Inter + JetBrains Mono')
    print('=' * 50)

if __name__ == '__main__':
    main()
